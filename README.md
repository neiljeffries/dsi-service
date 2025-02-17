# DSI-service

What does this thing do?

This python script (DSI-service.py) gets compiled into an exe file for Windows.

It runs a lightweight flask server which exposes the machine name at an endpoint:

Endpoint: <http://localhost:5000/machine-name>

## Install Python

If not installed, download and install Python from python.org.

Run these commands in PowerShell or CDM:

    python --version
    pip install pyinstaller
    pip install flask
    pip install flask-cors
    pip install pystray pillow

## Compile into a Windows .exe file

In PowerShell or CMD, navigate the the directory containing DSI-service.py & config.json files, then run one of the following commands, depending on your preference:

Create a folder with all files, config.json file is externally configurable. (Recommended)

    pyinstaller --add-data "config.json;." --noconsole DSI-service.py

DSI-service.exe will be in the "dist\DSI-service" folder.

The config.json file will be located in "dist\\DSI-service\\_internal" folder.

-- OR --

Create a stand alone .exe file with compiled config inside it

    pyinstaller --onefile --add-data "config.json;." --noconsole DSI-service.py

DSI-service.exe will be in the "dist" folder (config embedded).


## Angular component code example

    export class AppComponent implements AfterViewInit {
    
    machineName: string = '';
    
    constructor(private userService: UserService) { }

        ngOnInit(): void {
            this.userService.getMachineName().subscribe(
            data => {
                this.machineName = data;
                console.log(this.machineName)
            },
            error => {
                console.error('Error fetching machine name, make sure the Windows service is running on the local machine', error);
            }
            );
        }

    }

## Angular service code example

    getMachineName(): Observable<any> {
        return this.http.get<any>('<http://localhost:5000/machine-name>');
    }
