from django.db import models

class Scheme_AUM_Process(models.Model):
    amc = models.TextField()
    file_name = models.TextField()
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def updateFile(self, file):
        Scheme_AUM_Process.objects.filter(pk=self.id).update(
            file_name=file)

    def addCritical(self, log):
        log = Scheme_AUM_Process_Log(
            process=self,
            log=log,
            level="CRITIAL"
        )
        log.save()

    def addLog(self, log):
        log = Scheme_AUM_Process_Log(
            process=self,
            log=log,
            level="LOG"
        )
        log.save()

    def setAMC(self, amc):
        Scheme_AUM_Process.objects.filter(pk=self.id).update(
            amc=amc)


class Scheme_AUM_Process_Log(models.Model):
    process = models.ForeignKey(
        'Scheme_AUM_Process',
        on_delete=models.CASCADE
    )
    log = models.TextField()
    level = models.CharField(max_length=255)


class Scheme_AUM(models.Model):
    scheme = models.ForeignKey(
        'todo.Scheme',
        on_delete=models.CASCADE
    )
    date = models.DateField()
    aum = models.FloatField()

class Scheme_TER_Process(models.Model):
    amc = models.TextField()
    file_name = models.TextField()
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def updateFile(self, file):
        Scheme_TER_Process.objects.filter(pk=self.id).update(
            file_name=file)

    def addCritical(self, log):
        log = Scheme_TER_Process_Log(
            process=self,
            log=log,
            level="CRITIAL"
        )
        log.save()

    def addLog(self, log):
        log = Scheme_TER_Process_Log(
            process=self,
            log=log,
            level="LOG"
        )
        log.save()

    def setAMC(self, amc):
        Scheme_TER_Process.objects.filter(pk=self.id).update(
            amc=amc)


class Scheme_TER_Process_Log(models.Model):
    process = models.ForeignKey(
        'Scheme_TER_Process',
        on_delete=models.CASCADE
    )
    log = models.TextField()
    level = models.CharField(max_length=255)


class Scheme_TER(models.Model):
    scheme = models.ForeignKey(
        'todo.Scheme',
        on_delete=models.CASCADE
    )
    date = models.DateField()
    ter = models.FloatField()


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
