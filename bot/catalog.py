from dataclasses import dataclass

BUSINESS_NAME = "North Cut"
BUSINESS_ADDRESS = "Москва, ул. Большая Дмитровка, 21с2"
BUSINESS_HOURS = "Ежедневно с 10:00 до 20:00"


@dataclass(frozen=True)
class Service:
    id: str
    title: str
    price: int

    @property
    def price_label(self) -> str:
        return f"{self.price} ₽"

    @property
    def label(self) -> str:
        return f"{self.title} — {self.price_label}"


SERVICES: dict[str, Service] = {
    service.id: service
    for service in (
        Service(id="haircut", title="✂️ Мужская стрижка", price=1500),
        Service(id="haircut_beard", title="🧔 Стрижка + борода", price=2200),
        Service(id="kids", title="👦 Детская стрижка", price=1200),
        Service(id="beard", title="🪒 Оформление бороды", price=1000),
        Service(id="styling", title="💇 Укладка", price=700),
        Service(id="gray_camo", title="🧴 Камуфляж седины", price=1300),
        Service(id="north_cut_combo", title=f"👑 Комплекс {BUSINESS_NAME}", price=2800),
    )
}
