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
    
    # We can rely on a default "estimate.html" or one defined in shop.pdf_template_data
    # For now, we use the local file template
    template = env.get_template("estimate.html")
    
    # Временно: берем язык из настроек магазина, если у estimate.user нет загруженного отношения
    lang = shop.default_language
    
    rendered_html = template.render(
        estimate=estimate,
        shop=shop,
        items=estimate.items,
        t=lambda key: t(key, lang)
    )
    
    pdf_bytes = HTML(string=rendered_html).write_pdf()
    return pdf_bytes
