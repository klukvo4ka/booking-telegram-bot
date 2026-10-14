from dataclasses import dataclass


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
    )
}
