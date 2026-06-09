from app.models.contact_request import ContactRequest


def build_new_lead_email_body(contact: ContactRequest) -> str:
    company_value = contact.company or "No especificada"
    phone_value = contact.phone or "No especificado"

    return (
        "Nombre: {name}\n"
        "Empresa: {company}\n"
        "Correo: {email}\n"
        "Telefono: {phone}\n"
        "Mensaje:\n{message}\n"
    ).format(
        name=contact.name,
        company=company_value,
        email=contact.email,
        phone=phone_value,
        message=contact.message,
    )
