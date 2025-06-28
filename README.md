# DSI-service

What does this thing do?

This python script (DSI-service.py) gets compiled into an exe file for Windows.

It runs a lightweight flask server which exposes the machine name at an endpoint:

Endpoint: <http://localhost:5000/machine-name>

## Install Python

If not installed, download and install Python from python.org.

Once you have Python installed, run these commands in PowerShell or CMD:

```cmd
python --version
pip install pyinstaller
pip install flask
pip install flask-cors
pip install pystray pillow
```

## Compile into a Windows .exe file

In PowerShell or CMD, navigate to the directory containing DSI-service.py & config.json files, then run one of the following commands, depending on your preference:

**Create a folder with all files, config.json file is externally configurable. (Recommended)**

```cmd
pyinstaller --add-data "config.json;." --noconsole DSI-service.py
```

DSI-service.exe will be in the "dist\DSI-service" folder.

The config.json file will be located in "dist\\DSI-service\\_internal" folder.

-- OR --

**Create a stand alone .exe file with compiled config inside it**

<span style="color:red">WARNING:</span>  You might need to add "dsi-service.exe" to the exceptions list for your antivirus when building the **stand alone .exe**.
```cmd
pyinstaller --onefile --add-data "config.json;." --noconsole DSI-service.py
```

DSI-service.exe will be in the "dist" folder (config embedded).


Batch Files:
You can also use the .bat files in the root of this project to build a folder version or stand alone version of dsi-service.
 - build.bat will build the folder version.
 - build_stand_alone.bat will build the stand alone version.

Both methods will output to versioned folders in the dist/ directory.

## Angular component code example

```typescript
    export class AppComponent implements AfterViewInit {

    export class DsiMachineInfo {
        machine_name!: string;
        user_id!: string;
    }

    constructor(private userService: UserService) { }

        ngOnInit(): void {
            this.userService.getMachineName().subscribe(
                (data: DsiMachineInfo) => {
                    // Use user_id and machine_name as needed
                    console.log('User ID:', data.user_id);
                    console.log('Machine Name:', data.machine_name);
                },
                (error) => {
                    const errorMsg = error?.message ?? error?.statusText ?? 'Unknown error';
                    this.snackBar.open(
                        `Problem fetching machine name.\nMake sure the DSI Windows service is running on the local machine.\nError: ${errorMsg}`,
                        'Close',
                        { duration: 5000 }
                    );
                    console.error(
                        'Error fetching machine name, make sure the DSI Windows service is running on the local machine',
                        error
                    );
                }
            );
        }

    }
```

## Angular service code example

```typescript
    getMachineName(): Observable<any> {
        return this.http.get<any>('<http://localhost:5000/machine-name>');
    }
```
