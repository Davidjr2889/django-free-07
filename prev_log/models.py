from django.db import models


class Product(models.Model):
    """
    Produtos
    """

    empresa = models.CharField(max_length=2)
    # Brand Owner
    bo = models.CharField(max_length=50, blank=True, null=True)
    familia = models.CharField(max_length=100, blank=True, null=True)
    artigo = models.CharField(max_length=50)
    descricao = models.CharField(max_length=200, blank=True, null=True)
    # [M | N] M -> está em planeamento de compras ; N -> não está
    planingsys = models.CharField(max_length=1, blank=True, null=True)

    lead_time = models.IntegerField(blank=True, null=True)
    min_ordr_qty = models.DecimalField(
        max_digits=19, decimal_places=6, blank=True, null=True
    )
    # intervalos/múltiplos de quanto posso encomendar acima de min_ordr_qty
    ordr_multi = models.DecimalField(
        max_digits=19, decimal_places=6, blank=True, null=True
    )

    stock_minimo = models.DecimalField(
        max_digits=38, decimal_places=6, blank=True, null=True
    )
    stock_actual = models.DecimalField(
        max_digits=38, decimal_places=6, blank=True, null=True
    )
    stock_reservado = models.DecimalField(
        max_digits=38, decimal_places=6, blank=True, null=True
    )
    stock_encomendado = models.DecimalField(
        max_digits=38, decimal_places=6, blank=True, null=True
    )

    class Meta:
        unique_together = (
            (
                "empresa",
                "artigo",
            ),
        )
        db_table = "prev_log_product"


class Purchase(models.Model):
    """
    Dados de Compras desde 01/01/2021
    """

    empresa = models.CharField(max_length=2)
    # Brand Owner
    bo = models.CharField(max_length=50)
    fornecedor = models.CharField(max_length=100)
    familia = models.CharField(max_length=100)
    artigo = models.CharField(max_length=50)
    descricao = models.CharField(max_length=200, blank=True, null=True)

    # data do documento
    docdate = models.DateField()
    anodocdate = models.IntegerField()
    mesdocdate = models.IntegerField()
    # ---
    # data a que se refere o documento (data da fatura do fornecedor)
    taxdate = models.DateField()

    ano = models.IntegerField()
    mes = models.IntegerField()

    # qtd em unidades
    qt_u = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas
    qt_cx = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas de 9 litros
    qt_cx9 = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = (
            ("empresa", "bo", "fornecedor", "artigo", "docdate", "taxdate"),
        )
        db_table = "prev_log_purchase"


class Stock(models.Model):
    """
    Stock por armazém ao final de cada mês desde 01/01/2021
    """

    dia = models.DateField()
    empresa = models.CharField(max_length=2)
    # Brand Owner
    bo = models.CharField(max_length=50)
    marca = models.CharField(max_length=100)
    rotulo = models.CharField(max_length=100)
    familia = models.CharField(max_length=100)
    artigo = models.CharField(max_length=50)
    descricao = models.CharField(max_length=200, blank=True, null=True)

    armazem = models.CharField(max_length=8)

    # qtd em unidades
    stock_u = models.DecimalField(
        max_digits=17, decimal_places=2, blank=True, null=True
    )
    # qtd em caixas
    stock_cx = models.DecimalField(
        max_digits=17, decimal_places=2, blank=True, null=True
    )
    # qtd em caixas de 9 litros
    stock_cx9 = models.DecimalField(
        max_digits=17, decimal_places=2, blank=True, null=True
    )

    class Meta:
        unique_together = (("dia", "empresa", "bo", "artigo", "armazem"),)
        db_table = "prev_log_stock"


class Sale(models.Model):
    """
    Vendas ao final de cada mês desde 01/01/2021
    """

    empresa = models.CharField(max_length=2)
    # Brand Owner
    bo = models.CharField(max_length=50)
    canal = models.CharField(max_length=100)
    nome = models.CharField(max_length=100)
    familia = models.CharField(max_length=100)
    artigo = models.CharField(max_length=50)
    descricao = models.CharField(max_length=200, blank=True, null=True)
    capacidade = models.DecimalField(
        max_digits=19, decimal_places=6, blank=True, null=True
    )

    ano = models.IntegerField()
    mes = models.IntegerField()

    # qtd em unidades
    qt_u = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas
    qt_cx = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas de 9 litros
    qt_cx9 = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = (("empresa", "bo", "canal", "nome", "artigo", "ano", "mes"),)
        db_table = "prev_log_sale"


class OrigemPrevisao(models.Model):
    AUTO = 1
    MANUAL = 2

    designacao = models.IntegerField(default=1)

    class Meta:
        db_table = "prev_log_origem"
        verbose_name = "Origem Operação"
        verbose_name_plural = "Origens Operação"

    def __str__(self):
        return str(self.designacao)


class Tendency(models.Model):
    """
    Previsao de Vendas ao final de cada a partir do mes atual
    """

    empresa = models.CharField(max_length=2)
    bo = models.CharField(max_length=50, blank=True, null=True)
    familia = models.CharField(max_length=100, blank=True, null=True)
    artigo = models.CharField(max_length=50)

    # tendencia ponderada
    tendencia_ponderada = models.DecimalField(
        max_digits=17, decimal_places=4, blank=True, null=True
    )

    # base
    base_anual = models.DecimalField(
        max_digits=17, decimal_places=4, blank=True, null=True
    )

    # anual
    media_anual = models.DecimalField(
        max_digits=17, decimal_places=2, blank=True, null=True
    )
    tendencia_anual = models.DecimalField(
        max_digits=17, decimal_places=4, blank=True, null=True
    )

    # trimestral
    media_trimestral = models.DecimalField(
        max_digits=17, decimal_places=2, blank=True, null=True
    )
    tendencia_trimestral = models.DecimalField(
        max_digits=17, decimal_places=4, blank=True, null=True
    )

    class Meta:
        unique_together = (("artigo", "familia", "empresa", "bo"),)
        db_table = "prev_log_tendency"


class OpenOrder(models.Model):
    """
    Ordens de compra em aberto
    Quantidades encomendadas a fornecedores e ainda não recebidas
    """

    empresa = models.CharField(max_length=2)
    # Brand Owner
    bo = models.CharField(max_length=50)
    fornecedor = models.CharField(max_length=100)
    familia = models.CharField(max_length=100)
    artigo = models.CharField(max_length=50)
    descricao = models.CharField(max_length=200, blank=True, null=True)
    previsao_data_entrega = models.DateTimeField()

    ano = models.IntegerField()
    mes = models.IntegerField()

    # qtd em unidades
    qt_u = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas
    qt_cx = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas de 9 litros
    qt_cx9 = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = (
            (
                "empresa",
                "bo",
                "fornecedor",
                "artigo",
                "previsao_data_entrega",
                "ano",
                "mes",
            ),
        )
        db_table = "prev_log_open_order"


class BasicAgreement(models.Model):
    """
    Quantidades de compras acordadas com o BO para o ano
    """

    empresa = models.CharField(max_length=2)
    # Brand Owner
    bo = models.CharField(max_length=50)

    # código do fornecedor
    cardcode = models.CharField(max_length=15)
    fornecedor = models.CharField(max_length=100)

    familia = models.CharField(max_length=100)
    artigo = models.CharField(max_length=50)
    descricao = models.CharField(max_length=200, blank=True, null=True)
    numero_encomenda = models.CharField(max_length=19)
    data_encomenda = models.DateTimeField()
    previsao_data_envio = models.DateTimeField()
    previsao_data_entrega = models.DateTimeField()

    ano = models.IntegerField()
    mes = models.IntegerField()
    qt_encomendada = models.DecimalField(
        max_digits=19, decimal_places=6, blank=True, null=True
    )

    # qtd em unidades
    qt_u = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas
    qt_cx = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas de 9 litros
    qt_cx9 = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = (
            (
                "empresa",
                "bo",
                "cardcode",
                "fornecedor",
                "artigo",
                "numero_encomenda",
                "data_encomenda",
                "previsao_data_envio",
                "previsao_data_entrega",
            ),
        )
        db_table = "prev_log_basic_agreement"


########################
#   Log
########################


class ForecastManualChangeLog(models.Model):
    """
    Requisições de mudança de Stock
    """

    # Product Identification
    empresa = models.CharField(max_length=2)
    bo = models.CharField(max_length=50, blank=True, null=True)
    familia = models.CharField(max_length=100, blank=True, null=True)
    artigo = models.CharField(max_length=50)

    parent_request = models.ForeignKey("self", default=None, null=True, blank=True)
    created_at = models.DateTimeField()

    # Target forecast
    ano = models.IntegerField()
    mes = models.IntegerField()

    # Forecast model affected by the request
    origem_forecast = models.CharField(max_length=20)
    status = models.CharField(max_length=20)

    # user who requested and why
    utilizador_id = models.BigIntegerField()
    utilizador = models.CharField(max_length=50)
    comentario = models.TextField()

    # qtd em unidades
    qt_u = models.DecimalField(max_digits=17, decimal_places=4, blank=True, null=True)
    # qtd em caixas
    qt_cx = models.DecimalField(max_digits=17, decimal_places=4, blank=True, null=True)
    # qtd em caixas de 9 litros
    qt_cx9 = models.DecimalField(max_digits=17, decimal_places=4, blank=True, null=True)

    # Quantidades anteriores
    prev_qt_u = models.DecimalField(
        max_digits=17, decimal_places=4, blank=False, null=False
    )
    # qtd em caixas
    prev_qt_cx = models.DecimalField(
        max_digits=17, decimal_places=4, blank=False, null=False
    )
    # qtd em caixas de 9 litros
    prev_qt_cx9 = models.DecimalField(
        max_digits=17, decimal_places=4, blank=False, null=False
    )

    class Meta:
        unique_together = (
            (
                "artigo",
                "familia",
                "bo",
                "empresa",
                "ano",
                "mes",
                "created_at",
                "utilizador",
            ),
        )
        db_table = "prev_log_manual_change_log"


########################
#   Sale
########################


class SaleForecast(models.Model):
    """
    Previsao de Vendas ao final de cada a partir do mes atual
    """

    empresa = models.CharField(max_length=2)
    bo = models.CharField(max_length=50, blank=True, null=True)
    familia = models.CharField(max_length=100, blank=True, null=True)
    artigo = models.CharField(max_length=50)

    # Campo de origem da previsão pode ser feita pelo utilizador ('manual') ou pelo sistema ('auto')
    origem = models.ForeignKey(OrigemPrevisao)

    ano = models.IntegerField()
    mes = models.IntegerField()

    # qtd em unidades
    qt_u = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas
    qt_cx = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas de 9 litros
    qt_cx9 = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = (("artigo", "familia", "bo", "empresa", "ano", "mes"),)
        db_table = "prev_log_sale_forecast"


class SaleForecastOpenRequest(models.Model):
    """
    Requisições de mudança de Vendas
    """

    empresa = models.CharField(max_length=2)
    bo = models.CharField(max_length=50, blank=True, null=True)
    familia = models.CharField(max_length=100, blank=True, null=True)
    artigo = models.CharField(max_length=50)

    ano = models.IntegerField()
    mes = models.IntegerField()

    # user who requested and why
    utilizador_id = models.BigIntegerField()
    utilizador = models.CharField(max_length=50)
    comentario = models.TextField()
    created_at = models.DateTimeField()
    log = models.ForeignKey(ForecastManualChangeLog)

    # qtd em unidades
    qt_u = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas
    qt_cx = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas de 9 litros
    qt_cx9 = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = (
            (
                "artigo",
                "familia",
                "bo",
                "empresa",
                "ano",
                "mes",
                "utilizador",
                "created_at",
            ),
        )
        db_table = "prev_log_request_sale_forecast"


########################
#   Stock
########################


class StockForecast(models.Model):
    """
    Previsao de Stock ao final de cada a partir do mes atual
    """

    empresa = models.CharField(max_length=2)
    bo = models.CharField(max_length=50, blank=True, null=True)
    familia = models.CharField(max_length=100, blank=True, null=True)
    artigo = models.CharField(max_length=50)

    ano = models.IntegerField()
    mes = models.IntegerField()

    # Campo de origem da previsão pode ser feita pelo utilizador ('manual') ou pelo sistema ('auto')
    origem = models.ForeignKey(OrigemPrevisao)

    # qtd em unidades
    qt_u = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas
    qt_cx = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas de 9 litros
    qt_cx9 = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = (("artigo", "familia", "bo", "empresa", "ano", "mes"),)
        db_table = "prev_log_stock_forecast"


class StockForecastOpenRequest(models.Model):
    """
    Requisições de mudança de Stock
    """

    empresa = models.CharField(max_length=2)
    bo = models.CharField(max_length=50, blank=True, null=True)
    familia = models.CharField(max_length=100, blank=True, null=True)
    artigo = models.CharField(max_length=50)

    ano = models.IntegerField()
    mes = models.IntegerField()

    # user who requested and why
    utilizador_id = models.BigIntegerField()
    utilizador = models.CharField(max_length=50)
    comentario = models.TextField()
    created_at = models.DateTimeField()
    log = models.ForeignKey(ForecastManualChangeLog)

    # qtd em unidades
    qt_u = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas
    qt_cx = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas de 9 litros
    qt_cx9 = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = (
            (
                "artigo",
                "familia",
                "bo",
                "empresa",
                "ano",
                "mes",
                "utilizador",
                "created_at",
            ),
        )
        db_table = "prev_log_request_stock_forecast"


########################
#   Purchase
########################


class PurchaseForecast(models.Model):
    empresa = models.CharField(max_length=2)
    bo = models.CharField(max_length=50, blank=True, null=True)
    familia = models.CharField(max_length=100, blank=True, null=True)
    artigo = models.CharField(max_length=50)

    ano = models.IntegerField()
    mes = models.IntegerField()

    origem = models.ForeignKey(OrigemPrevisao)

    data_limite_pedido = models.DateTimeField()

    qt_u = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    qt_cx = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    qt_cx9 = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = (("artigo", "familia", "bo", "empresa", "ano", "mes"),)
        db_table = "prev_log_purchase_forecast"


class PurchaseForecastOpenRequest(models.Model):
    """
    Requisições de mudança de Stock
    """

    empresa = models.CharField(max_length=2)
    bo = models.CharField(max_length=50, blank=True, null=True)
    familia = models.CharField(max_length=100, blank=True, null=True)
    artigo = models.CharField(max_length=50)

    ano = models.IntegerField()
    mes = models.IntegerField()

    # user who requested and why
    utilizador_id = models.BigIntegerField()
    utilizador = models.CharField(max_length=50)
    comentario = models.TextField()
    created_at = models.DateTimeField()
    log = models.ForeignKey(ForecastManualChangeLog)

    # qtd em unidades
    qt_u = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas
    qt_cx = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas de 9 litros
    qt_cx9 = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = (
            (
                "artigo",
                "familia",
                "bo",
                "empresa",
                "ano",
                "mes",
                "utilizador",
                "created_at",
            ),
        )
        db_table = "prev_log_request_purchase_forecast"


########################
#   Orders
########################


class ApprovedOrderRequests(models.Model):
    """
    Requisições de mudança de Stock
    """

    empresa = models.CharField(max_length=2)
    bo = models.CharField(max_length=50, blank=True, null=True)
    familia = models.CharField(max_length=100, blank=True, null=True)
    artigo = models.CharField(max_length=50)

    data_do_pedido = models.DateField()

    # user who requested and why
    utilizador_id = models.BigIntegerField()
    utilizador = models.CharField(max_length=50)
    created_at = models.DateTimeField()

    # qtd em unidades
    qt_u = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas
    qt_cx = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    # qtd em caixas de 9 litros
    qt_cx9 = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = "prev_log_approved_orders"
