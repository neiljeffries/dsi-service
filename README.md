# dsi-service


If not installed, download and install Python from python.org.

python --version

- pip install pyinstaller
- pip install flask
- pip install flask-cors
- pip install pystray pillow

## Compile into a Windows .exe file
# In PowerShell or CMD and run: 

### Creates a folder with all files, including external config.json file. (Recommended)
pyinstaller --add-data "config.json;." --noconsole DSI-service.py

### Creates a stand alone .exe file with compiled config
pyinstaller --onefile --add-data "config.json;." --noconsole DSI-service.py
-or-


Endpoint: http://localhost:5000/machine-name




# angular component code
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

# angular service code
  getMachineName(): Observable<any> {
    return this.http.get<any>('http://localhost:5000/machine-name');
  }