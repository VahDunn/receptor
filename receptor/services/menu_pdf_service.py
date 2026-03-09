from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from receptor.api.schemas.menu import MenuOut


class MenuPdfService:
    def __init__(self) -> None:
        self._font_name = self._register_fonts()
        self._font_name_bold = self._font_name
        self._styles = self._build_styles()

    def build_pdf(self, menu: MenuOut) -> bytes:
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
            title=f"Меню #{menu.id}",
            author="Receptor",
        )

        story: list[Any] = []

        story.extend(self._build_header(menu))
        story.extend(self._build_summary(menu))
        story.extend(self._build_daily_kcal(menu))
        story.extend(self._build_menu_days(menu))
        story.extend(self._build_products_table(menu))

        doc.build(story)

        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    def _register_fonts(self) -> str:
        candidates = [
            ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans"),
            ("/usr/share/fonts/dejavu/DejaVuSans.ttf", "DejaVuSans"),
        ]

        for path, font_name in candidates:
            try:
                pdfmetrics.registerFont(TTFont(font_name, path))
                return font_name
            except Exception:
                continue

        return "Helvetica"

    def _build_styles(self) -> dict[str, ParagraphStyle]:
        styles = getSampleStyleSheet()

        return {
            "title": ParagraphStyle(
                name="MenuTitle",
                parent=styles["Heading1"],
                fontName=self._font_name_bold,
                fontSize=18,
                leading=22,
                alignment=TA_CENTER,
                spaceAfter=8,
                textColor=colors.HexColor("#1F2937"),
            ),
            "subtitle": ParagraphStyle(
                name="MenuSubtitle",
                parent=styles["Normal"],
                fontName=self._font_name,
                fontSize=9,
                leading=12,
                alignment=TA_CENTER,
                spaceAfter=14,
                textColor=colors.HexColor("#6B7280"),
            ),
            "section": ParagraphStyle(
                name="MenuSection",
                parent=styles["Heading2"],
                fontName=self._font_name_bold,
                fontSize=12,
                leading=15,
                spaceBefore=8,
                spaceAfter=8,
                textColor=colors.HexColor("#111827"),
            ),
            "body": ParagraphStyle(
                name="MenuBody",
                parent=styles["BodyText"],
                fontName=self._font_name,
                fontSize=9.5,
                leading=13,
                textColor=colors.HexColor("#1F2937"),
                spaceAfter=4,
            ),
            "small": ParagraphStyle(
                name="MenuSmall",
                parent=styles["BodyText"],
                fontName=self._font_name,
                fontSize=8.5,
                leading=11,
                textColor=colors.HexColor("#4B5563"),
            ),
            "day_title": ParagraphStyle(
                name="MenuDayTitle",
                parent=styles["Heading3"],
                fontName=self._font_name_bold,
                fontSize=10.5,
                leading=13,
                spaceAfter=5,
                textColor=colors.HexColor("#0F172A"),
            ),
            "dish": ParagraphStyle(
                name="MenuDish",
                parent=styles["BodyText"],
                fontName=self._font_name,
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#111827"),
                leftIndent=6,
                bulletIndent=0,
            ),
        }

    def _build_header(self, menu: MenuOut) -> list[Any]:
        title = Paragraph(f"Недельное меню #{menu.id}", self._styles["title"])

        created_at = str(menu.created_at) if menu.created_at else "-"
        store = self._safe_get(menu.menu_meta, "store", "-")
        city = self._safe_get(menu.menu_meta, "city", "-")

        subtitle = Paragraph(
            f"Магазин: {store} | Город: {city} | Создано: {created_at}",
            self._styles["subtitle"],
        )

        return [title, subtitle]

    def _build_summary(self, menu: MenuOut) -> list[Any]:
        heading = Paragraph("Сводка", self._styles["section"])

        kcal_min = self._safe_get(menu.calorie_target, "min_kcal_per_day", "-")
        kcal_max = self._safe_get(menu.calorie_target, "max_kcal_per_day", "-")

        summary_data = [
            ["Недельный бюджет", f"{menu.max_money_rub} ₽"],
            ["Допуск по бюджету", f"{menu.weekly_budget_tolerance_rub} ₽"],
            ["Оценка стоимости за неделю", f"{menu.weekly_cost_estimate_rub} ₽"],
            ["Цель по калориям в день", f"{kcal_min} - {kcal_max} ккал"],
            ["Количество продуктов", str(len(menu.products_with_quantities))],
        ]

        table = Table(
            summary_data,
            colWidths=[65 * mm, 85 * mm],
            hAlign="LEFT",
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#111827")),
                    ("FONTNAME", (0, 0), (0, -1), self._font_name_bold),
                    ("FONTNAME", (1, 0), (1, -1), self._font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("LEADING", (0, 0), (-1, -1), 12),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#94A3B8")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        return [heading, table, Spacer(1, 6 * mm)]

    def _build_daily_kcal(self, menu: MenuOut) -> list[Any]:
        heading = Paragraph("Калории по дням", self._styles["section"])

        kcal_rows = [["День", "Оценка ккал"]]
        kcal_rows.extend(
            [
                [str(index + 1), str(value)]
                for index, value in enumerate(menu.daily_kcal_estimates)
            ]
        )

        table = Table(
            kcal_rows,
            colWidths=[28 * mm, 42 * mm],
            hAlign="LEFT",
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                    ("FONTNAME", (0, 0), (-1, 0), self._font_name_bold),
                    ("FONTNAME", (0, 1), (-1, -1), self._font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("LEADING", (0, 0), (-1, -1), 12),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )

        return [heading, table, Spacer(1, 6 * mm)]

    def _build_menu_days(self, menu: MenuOut) -> list[Any]:
        story: list[Any] = [Paragraph("Меню по дням", self._styles["section"])]

        for day in menu.menu_structure:
            day_number = self._safe_get(day, "day", "-")
            story.append(Paragraph(f"День {day_number}", self._styles["day_title"]))

            story.extend(self._build_meal_block("Завтрак", day.get("breakfast", [])))
            story.extend(self._build_meal_block("Обед", day.get("lunch", [])))
            story.extend(self._build_meal_block("Ужин", day.get("dinner", [])))

            story.append(Spacer(1, 4 * mm))

        return story

    def _build_meal_block(
        self, meal_name: str, dishes: list[dict[str, Any]]
    ) -> list[Any]:
        block: list[Any] = [Paragraph(f"<b>{meal_name}</b>", self._styles["body"])]

        if not dishes:
            block.append(Paragraph("— блюд нет", self._styles["small"]))
            return block

        for dish in dishes:
            dish_name = self._safe_get(dish, "dish_name", "Без названия")
            products = dish.get("products", [])
            products_text = (
                ", ".join(str(product_id) for product_id in products)
                if products
                else "-"
            )

            block.append(Paragraph(f"— {dish_name}", self._styles["dish"]))
            block.append(
                Paragraph(
                    f"ID продуктов: {products_text}",
                    self._styles["small"],
                )
            )

        return block

    def _build_products_table(self, menu: MenuOut) -> list[Any]:
        heading = Paragraph("Продукты и количества", self._styles["section"])

        rows: list[list[Any]] = [["ID", "Продукт", "Ед.", "Кол-во"]]

        for item in menu.products_with_quantities:
            product_name = item.product.name if item.product else "-"
            rows.append(
                [
                    str(item.product_id),
                    Paragraph(product_name, self._styles["small"]),
                    item.unit,
                    str(item.quantity),
                ]
            )

        table = Table(
            rows,
            colWidths=[18 * mm, 88 * mm, 22 * mm, 28 * mm],
            repeatRows=1,
            hAlign="LEFT",
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCEAF7")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                    ("FONTNAME", (0, 0), (-1, 0), self._font_name_bold),
                    ("FONTNAME", (0, 1), (-1, -1), self._font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("LEADING", (0, 0), (-1, -1), 11),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("ALIGN", (2, 0), (3, -1), "CENTER"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        return [heading, table]

    @staticmethod
    def _safe_get(data: dict[str, Any], key: str, default: Any) -> Any:
        return data.get(key, default) if isinstance(data, dict) else default
