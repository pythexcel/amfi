from django.db import models


class Scheme_Portfolio_Data(models.Model):
    scheme = models.ForeignKey(
        'todo.Scheme',
        on_delete=models.CASCADE
    )
    url = models.TextField()
    date = models.DateField()
    parsed = models.BooleanField(default=False, null=False)


class Scheme_Portfolio(models.Model):
    scheme = models.ForeignKey(
        'Scheme_Portfolio_Data',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    isin = models.CharField(max_length=255)
    quantity = models.CharField(max_length=255)
    coupon = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    rating = models.CharField(max_length=255)
    market = models.CharField(max_length=255)
    percent = models.CharField(max_length=255)


class AMC_Portfolio_ProcessManager(models.Manager):
    def get_portfolio_to_process(self, limit=1):
        return self.filter(processed=True, parsed=False).order_by('-date')[:limit]


class AMC_Portfolio_Process(models.Model):
    amc = models.TextField()
    file_name = models.TextField()
    # this is a flag to check if file was identifyed for year/date/amc
    processed = models.BooleanField(default=False)
    date = models.DateTimeField(null=False, auto_now_add=True)
    final_path = models.TextField(default="")
    # this is a flag to identify if actual portfolio is parsed or not
    parsed = models.BooleanField(default=False)

    objects = AMC_Portfolio_ProcessManager()

    def parsing_completed(self):
        AMC_Portfolio_Process.objects.filter(pk=self.id).update(
            parsed=True)

    def setFinalFilePath(self, path):
        AMC_Portfolio_Process.objects.filter(pk=self.id).update(
            final_path=path, parsed=False, processed=True)

    def addCritical(self, log):
        log = AMC_Portfolio_Process_Log(
            process=self,
            log=log,
            level="CRITIAL"
        )
        log.save()

    def addLog(self, log):
        log = AMC_Portfolio_Process_Log(
            process=self,
            log=log,
            level="LOG"
        )
        log.save()

    def setAMC(self, amc, processed=False):
        AMC_Portfolio_Process.objects.filter(pk=self.id).update(
            amc=amc, processed=processed)


class AMC_Portfolio_Process_Log(models.Model):
    process = models.ForeignKey(
        'AMC_Portfolio_Process',
        on_delete=models.CASCADE
    )
    log = models.TextField()
    level = models.CharField(max_length=255)
