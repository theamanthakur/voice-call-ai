# app/lead_store.py

leads = []


def save_lead(phone: str, message: str):

    leads.append({
        "phone": phone,
        "message": message,
    })


def get_leads():
    return leads