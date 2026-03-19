import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from app.models.estimate import Estimate
from app.models.shop import Shop
from app.core.i18n import t

def generate_pdf_from_estimate(estimate: Estimate, shop: Shop) -> bytes:
    """
    Renders an HTML template with the estimate and shop details,
    then generates a PDF and returns its bytes.
    """
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    
    template = env.get_template("estimate.html")
    
    lang = shop.default_language
    
    # Resolve logo_url to an absolute file path for WeasyPrint
    # WeasyPrint cannot follow relative web paths without a base_url
    app_dir = os.path.dirname(os.path.dirname(__file__))
    static_dir = os.path.join(app_dir, "static")
    base_url = f"file://{static_dir}/"
    
    # Provide the logo as an absolute file:// URL so WeasyPrint can embed it
    logo_file_url = None
    if shop.logo_url and shop.logo_url.startswith("/static/"):
        relative_path = shop.logo_url[len("/static/"):]
        abs_path = os.path.join(static_dir, relative_path)
        if os.path.exists(abs_path):
            logo_file_url = f"file://{abs_path}"
    elif shop.logo_url and shop.logo_url.startswith("http"):
        # External URL — pass as-is
        logo_file_url = shop.logo_url
    
    rendered_html = template.render(
        estimate=estimate,
        shop=shop,
        items=estimate.items,
        logo_file_url=logo_file_url,
        t=lambda key: t(key, lang)
    )
    
    pdf_bytes = HTML(string=rendered_html, base_url=base_url).write_pdf()
    return pdf_bytes
