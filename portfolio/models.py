from django.db import models

# Create your models here.

"""
we need to store data as follows
1. portfolio summary and assocation to a user account
2. portfolio logs etc for admin
3. portfolio detail i.e transaction, summary, fund, nav 
"""


class PortfolioAdmin(models.Model):
    # this is just for adming logs
    file_name = models.TextField()
    processed_file_name = models.TextField()
    password = models.TextField()
    date = models.DateTimeField(auto_now_add=True, blank=True)
    has_error = models.BooleanField()
    is_processed = models.BooleanField()

    def cleanLogs(self):
        PortfolioAdminLogs.objects.filter(portfolio_admin=self).delete()

    def addErrorLog(self, msg):
        logObj = PortfolioAdminLogs(
            portfolio_admin=self,
            log=msg
        )
        logObj.save()
        self.has_error = True
        self.save()


class PortfolioAdminLogs(models.Model):
    portfolio_admin = models.ForeignKey(
        'PortfolioAdmin',
        on_delete=models.CASCADE
    )
    log = models.TextField()


class Portfolio(models.Model):
    # user should come here but till now we don't have any user system implemented so skipping it
    email = models.TextField()
    mobile = models.TextField()

    pf_amc = None
    pf_folio = None
    pf_scheme = None

    def addAMC(self, amc):
        try:
            self.pf_amc = PortfolioAMC.objects.get(portfolio=self, amc=amc)
        except PortfolioAMC.DoesNotExist:
            p = PortfolioAMC(portfolio=self, amc=amc)
            p.save()
            self.pf_amc = p
        return self.pf_amc

    def addFolio(self, folio):
        try:
            self.pf_folio = PortfolioFolio.objects.get(
                portfolio_amc=self.pf_amc, folio=folio)
        except PortfolioFolio.DoesNotExist:
            p = PortfolioFolio(portfolio_amc=self.pf_amc, folio=folio)
            p.save()
            self.pf_folio = p
        return self.pf_folio

    def addFund(self, scheme):
        try:
            self.pf_scheme = PortfolioFolioFund.objects.get(
                portfolio_folio=self.pf_folio, fund_id=scheme)
        except PortfolioFolioFund.DoesNotExist:
            p = PortfolioFolioFund(portfolio_folio=self.pf_folio,
                                   fund_id=scheme)
            p.save()
            self.pf_scheme = p

        PortfolioFolioTrx.objects.filter(
            portfolio_folio=self.pf_folio).delete()
        return self.pf_scheme

    def addTrx(self, trx_obj):
        """
        trx = {
            "type": "MANUAL",
            "name": line,
            "date": trx_date,
            "amount": trx_amount,
            "price_per_unit": trx_price,
            "unit": trx_unit,
            "unit_balance": trx_balance,
            "trx_type": trx_type
        }

        trx = {
            "type": "AUTOMATIC",
            "name": actual_trx,
            "date": trx_date,
            "amount": trx_amount
        }
        """

        if trx_obj["type"] == "MANUAL":
            trx = PortfolioFolioTrx(
                portfolio_folio=self.pf_folio,
                trx_type=trx_obj["type"],
                trx_name=trx_obj["name"],
                trx_date=trx_obj["date"],
                trx_amount=trx_obj["amount"],
                trx_price_unit=trx_obj["price_per_unit"],
                trx_unit=trx_obj["unit"],
                unit_balance=trx_obj["unit_balance"],
                trx_amount_type=trx_obj["trx_type"],
            )
            trx.save()
        else:
            trx = PortfolioFolioTrx(
                portfolio_folio=self.pf_folio,
                trx_type=trx_obj["type"],
                trx_name=trx_obj["name"],
                trx_date=trx_obj["date"],
                trx_amount=trx_obj["amount"]
            )
            trx.save()
        pass


class PortfolioAMC(models.Model):
    amc = models.ForeignKey(
        'todo.AMC',
        on_delete=models.CASCADE
    )
    portfolio = models.ForeignKey(
        'Portfolio',
        on_delete=models.CASCADE
    )


class PortfolioFolio(models.Model):
    portfolio_amc = models.ForeignKey(
        'PortfolioAMC',
        on_delete=models.CASCADE
    )
    folio = models.TextField()


class PortfolioFolioFund(models.Model):
    portfolio_folio = models.ForeignKey(
        'PortfolioFolio',
        on_delete=models.CASCADE
    )
    fund_id = models.TextField()
    fund_text = models.TextField()


class PortfolioFolioTrx(models.Model):
    portfolio_folio = models.ForeignKey(
        'PortfolioFolio',
        on_delete=models.CASCADE
    )
    trx_type = models.TextField()
    trx_name = models.TextField()
    trx_date = models.DateField()
    trx_amount = models.FloatField()
    trx_price_unit = models.FloatField()
    trx_unit = models.FloatField()
    unit_balance = models.FloatField()
    trx_amount_type = models.TextField()
