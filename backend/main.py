from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openpyxl import load_workbook
from datetime import datetime
import io
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MarriageData(BaseModel):
    gFirst: str; gMiddle: str; gLast: str; gBday: str; gAge: int
    gBrgy: str; gTown: str; gProv: str; gCountry: str; gCitizen: str
    gStatus: str; gReligion: str
    gFathF: str; gFathM: str; gFathL: str
    gMothF: str; gMothM: str; gMothL: str
    gGiverF: str; gGiverM: str; gGiverL: str; gGiverRelation: str
    bFirst: str; bMiddle: str; bLast: str; bBday: str; bAge: int
    bBrgy: str; bTown: str; bProv: str; bCountry: str; bCitizen: str
    bStatus: str; bReligion: str
    bFathF: str; bFathM: str; bFathL: str
    bMothF: str; bMothM: str; bMothL: str
    bGiverF: str; bGiverM: str; bGiverL: str; bGiverRelation: str

def to_up(val):
    return str(val).upper().strip() if val else ""

# Added this so you can test in the browser!
@app.get("/")
async def root():
    return {"message": "Marriage System Backend is Running on Port 8080"}

@app.post("/generate-marriage-pack") # REMOVED the trailing slash here
async def generate_excel(data: MarriageData):
    m_age, f_age = data.gAge, data.bAge
    template = "application_only.xlsx"
    
    if f_age <= 20 and m_age >= 25: template = "consent_f.xlsx"
    elif m_age <= 20 and f_age >= 25: template = "consent_m.xlsx"
    elif m_age <= 20 and f_age <= 20: template = "consent_m_f.xlsx"
    elif 21 <= f_age <= 24 and m_age >= 25: template = "advice_f.xlsx"
    elif 21 <= m_age <= 24 and f_age >= 25: template = "advice_m.xlsx"
    elif 21 <= m_age <= 24 and 21 <= f_age <= 24: template = "advice_m_f.xlsx"
    elif 21 <= m_age <= 24 and f_age <= 20: template = "advice_m_consent_f.xlsx"
    elif 21 <= f_age <= 24 and m_age <= 20: template = "consent_m_advice_f.xlsx"

    template_path = os.path.join("templates", template)
    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail=f"File {template} missing in templates folder.")

    try:
        wb = load_workbook(template_path)
        now = datetime.now()
        gTownProv = to_up(f"{data.gTown}, {data.gProv}")
        bTownProv = to_up(f"{data.bTown}, {data.bProv}")
        gFullAddr = to_up(f"{data.gBrgy}, {data.gTown}, {data.gProv}")
        bFullAddr = to_up(f"{data.bBrgy}, {data.bTown}, {data.bProv}")
        
        isGroomExternal = gTownProv != "SOLANO, NUEVA VIZCAYA"
        isBrideExternal = bTownProv != "SOLANO, NUEVA VIZCAYA"

        for sheet in wb.worksheets:
            s_name = sheet.title.upper()
            if "ADDRESSBACKNOTICE" in s_name or "ENVELOPEADDRESS" in s_name:
                sheet.sheet_state = 'visible' if (isGroomExternal or isBrideExternal) else 'hidden'

            if "APPLICATION" in s_name:
                sheet['B8'], sheet['B9'], sheet['B10'] = to_up(data.gFirst), to_up(data.gMiddle), to_up(data.gLast)
                sheet['B11'], sheet['N11'] = data.gBday, data.gAge
                sheet['B12'], sheet['L12'] = gTownProv, to_up(data.gCountry)
                sheet['B13'], sheet['H13'] = "MALE", to_up(data.gCitizen)
                sheet['B15'], sheet['M15'] = gFullAddr, to_up(data.gCountry)
                sheet['B16'], sheet['B17'] = to_up(data.gReligion), to_up(data.gStatus)
                sheet['B22'], sheet['H22'], sheet['L22'] = to_up(data.gFathF), to_up(data.gFathM), to_up(data.gFathL)
                sheet['B26'], sheet['G26'], sheet['K26'] = to_up(data.gMothF), to_up(data.gMothM), to_up(data.gMothL)
                if 18 <= data.gAge <= 24:
                    sheet['B30'], sheet['H30'], sheet['L30'] = to_up(data.gGiverF), to_up(data.gGiverM), to_up(data.gGiverL)
                    sheet['B31'], sheet['B32'] = to_up(data.gGiverRelation), to_up(data.gCitizen)

                sheet['U8'], sheet['U9'], sheet['U10'] = to_up(data.bFirst), to_up(data.bMiddle), to_up(data.bLast)
                sheet['U11'], sheet['AF11'] = data.bBday, data.bAge
                sheet['U12'], sheet['AE12'] = bTownProv, to_up(data.bCountry)
                sheet['U13'], sheet['Z13'] = "FEMALE", to_up(data.bCitizen)
                sheet['U15'], sheet['AF15'] = bFullAddr, to_up(data.bCountry)
                sheet['U16'], sheet['U17'] = to_up(data.bReligion), to_up(data.bStatus)
                sheet['U22'], sheet['Y22'], sheet['AC22'] = to_up(data.bFathF), to_up(data.bFathM), to_up(data.bFathL)
                sheet['U26'], sheet['Y26'], sheet['AD26'] = to_up(data.bMothF), to_up(data.bMothM), to_up(data.bMothL)
                if 18 <= data.bAge <= 24:
                    sheet['U30'], sheet['Y30'], sheet['AD30'] = to_up(data.bGiverF), to_up(data.bGiverM), to_up(data.bGiverL)
                    sheet['U31'], sheet['U32'] = to_up(data.bGiverRelation), to_up(data.bCitizen)

                sheet['B34'], sheet['U34'] = gFullAddr, bFullAddr
                sheet['B37'], sheet['U37'], sheet['E37'], sheet['W37'] = now.day, now.day, now.strftime("%B").upper(), now.strftime("%B").upper()
                sheet['L37'], sheet['AD37'] = now.year, now.year

            if "NOTICE" in s_name:
                if isGroomExternal and isBrideExternal:
                    sheet['E44'], sheet['E45'] = gFullAddr, bFullAddr
                elif isGroomExternal:
                    sheet['E44'] = gFullAddr
                elif isBrideExternal:
                    sheet['E44'] = bFullAddr

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return Response(
            content=output.getvalue(), 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=MarriagePack.xlsx"}
        )
    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)