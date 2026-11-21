import os
if os.environ.get('QA_FAKE_HOUR'):
    try:
        from playwright.sync_api import Page
        import datetime
        _g=Page.goto
        def goto(self,*a,**k):
            if not getattr(self,'_fk',False):
                self._fk=True
                d=datetime.datetime.now().replace(hour=int(os.environ['QA_FAKE_HOUR']),minute=0,second=0,microsecond=0)
                self.clock.install(time=d)
            return _g(self,*a,**k)
        Page.goto=goto
    except Exception as e: print('fk fail',e)
