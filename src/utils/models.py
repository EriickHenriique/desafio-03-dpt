from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime
from typing import Any


class SalesData(BaseModel):
    order_id: str
    customer_id: str
    customer_name: str
    customer_segment: str
    customer_type: str
    first_purchase_date: datetime
    last_purchase_date: datetime
    product_id: str
    product_name: str
    category: str
    sub_category: str
    brand: str
    order_date: datetime
    quantity: int
    unit_price: float
    discount_pct: float
    sales_channel: str
    payment_method: str
    sales_rep: str
    region: str
    operating_expenses: float
    cash_balance: float
    debt_balance: float
    monthly_burn: float
    churn_flag: bool

    model_config = {"str_strip_whitespace": True}  # strip em todos os str automaticamente

    # Remove nulos em campos obrigatórios de texto
    @field_validator(
        "order_id", "customer_id", "customer_name", "customer_segment",
        "customer_type", "product_id", "product_name", "category",
        "sub_category", "brand", "sales_channel", "payment_method",
        "sales_rep", "region",
        mode="before",
    )
    @classmethod
    def reject_empty_strings(cls, v: Any) -> Any:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            raise ValueError("Campo obrigatório não pode ser nulo ou vazio.")
        return v

    # Garante que floats não sejam negativos onde não faz sentido 
    @field_validator("unit_price", "discount_pct", "operating_expenses", "monthly_burn", mode="before")
    @classmethod
    def non_negative_floats(cls, v: Any) -> Any:
        if v is not None and float(v) < 0:
            raise ValueError("Valor não pode ser negativo.")
        return v
    
    # Garante que quantity seja positivo
    @field_validator("quantity", mode="before")
    @classmethod
    def positive_quantity(cls, v: Any) -> Any:
        if v is not None and int(v) <= 0:
            raise ValueError("Quantidade deve ser maior que zero.")
        return v

    # Consistência entre datas
    @model_validator(mode="after")
    def check_date_consistency(self) -> "SalesData":
        if self.first_purchase_date > self.last_purchase_date:
            raise ValueError("first_purchase_date não pode ser posterior a last_purchase_date.")
        if self.order_date < self.first_purchase_date:
            raise ValueError("order_date não pode ser anterior a first_purchase_date.")
        return self 

