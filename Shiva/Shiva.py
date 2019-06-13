from dataclasses import dataclass, field
from typing import Dict, Tuple
import importlib

@dataclass
class Shiva:
    services  : Dict[str, bool] = field(default_factory=dict)
    verbose   : bool = False
    keepAlive : bool = True

    SERVICES_PATH = 'services'

 
    def verboseModeON(self) -> None:
        """Activate verbose mode
       
               :return: None
        """
        self.verbose = True


    def verboseModeOFF(self) -> None:
        """Deactivate verbose mode
       
               :return: None
        """
        self.verbose = True


    def keepAliveModeON(self) -> None:
        """Activate keepAlive mode
       
               :return: None
        """
        self.vkeepAlive = True


    def keepAliveModeOFF(self) -> None:
        """Deactivate keepAlive mode
       
               :return: None
        """
        self.keepAlive = False


    def start(self, *servicesList : Tuple[str]) -> None:
        """Import services
           Sample : Shiva.start('gmail', google_calendar')

               :param servicesList: List of services to start

               :return: None
        """
        for serviceName in servicesList:
            if self.verbose:
                print(f'Loading {serviceName}...', end=' ')
            try:
                module = importlib.import_module(Shiva.SERVICES_PATH + '.' + serviceName + '.' + serviceName)
                if serviceName in self.services:
                    print(f'Module {serviceName} already loaded')
                    if not self.keepAlive:
                        exit(1)
                else:
                    self.services[serviceName] = True
                    if self.verbose:
                        print('ok')
                classObject = getattr(module, serviceName[0].upper() + serviceName[1:])
                setattr(self, serviceName, classObject())

            except ModuleNotFoundError as error:
                if self.verbose:
                    print('error')
                else:
                    print(error)
                if not self.keepAlive:
                    exit(2)


    def list(self) -> None:
        """Display the list of services loaded
        
            :return: None
        """
        # __annotations__ et __doc__
        for serviceName in self.services.keys():
            print(f'- {serviceName}')


if __name__ == '__main__':
    service = Shiva()
    service.verboseModeON()
    service.start('gmail', 'google_calendar')
    service.gmail.requirements()
    service.gmail.expose()
    service.gmail.help('scope')
    service.list()
    service.gmail.init()
    service.gmail.sendMessage(fromUser='sender@adress.com', to='receiver@adress.com', subject='Test Shiva', message='Un petit coucou!')
