# DSI-service

DSI-service was created and tested on Windows 11.

DSI-service is a lightweight flask server that runs in the background on Windows. It provides the machine name and logged in user id to the endpoint "/machine-name".



***Flask Server Settings:***

Configurable in /config.json
 - Port: 5000
 - Endpoint: <http://localhost:5000/machine-name>

***Response Object***

```json
{
  "machine_name":"BOBS_COOL_PC",
  "user_id":"BOB"
}
```

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



## Use PyInstaller to compile the exe file for Windows

1. Open PowerShell or a CMD.

2. Navigate to this project directory, make sure you are in the same directory containing DSI-service.py & config.json files.

3. Run one of the following commands. There are 2 examples below: the first is for a folder build. The second is for a stand alone build.

#### Example 1

**Create a folder with all files**
- The ';config.json file is externally configurable with the folder build. (Recommended)**

```cmd
pyinstaller --add-data "config.json;." --noconsole DSI-service.py
```

By default, the DSI-service.exe will output to "dist\DSI-service" folder.

The config.json file will be located in "dist\\DSI-service\\_internal" folder.

-- OR --

#### Example 2

**Create a stand alone .exe file with compiled config inside it**

<span style="color:red">WARNING:</span>  You might need to add "dsi-service.exe" to the exceptions list for your antivirus when building the **stand alone .exe** with PyInstaller.
```cmd
pyinstaller --onefile --add-data "config.json;." --noconsole DSI-service.py
```

DSI-service.exe will be in the "dist" folder (config embedded).


***Batch Files:***
You can also use the .bat files in the root of this project to build a folder version or stand alone version of dsi-service.
 - Batch File: build.bat
    - builds the folder version.
 - Batch File: build_stand_alone.bat
    - builds the stand alone version.

Both batch scripts will output to versioned folders inside the dist/ directory.

## Integrating Angular with DSI-Service.exe

In the AppComponent we make the initial call to the DSI-Service endpoint running on the Windows machine.
 - Calls *this.userService.getMachineName()*

***AppComponent.ts***

```typescript
    export class AppComponent{

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

## Angular Service

In the Angular service we are creating a behavior subject to make data available for any components that need to subscribe.

***UserService.ts***

```typescript

export class UserService {
  private machineInfoSubject = new BehaviorSubject<MachineInfo | null>(null);
  public machineInfo$ = this.machineInfoSubject.asObservable();

  constructor(private http: HttpClient) {}

  getMachineInfo(): MachineInfo | null {
    return this.machineInfoSubject.value;
  }

  setMachineInfo(machineInfo: MachineInfo): void {
    this.machineInfoSubject.next(machineInfo);
  }

  getMachineName(): Observable<MachineInfo> {
    return this.http.get<MachineInfo>('http://localhost:5000/machine-name').pipe(
      tap(machineInfo => this.setMachineInfo(machineInfo))
    );
  }

}
```

#### How to subscribe to the behaviour subject in another component

Subscribe to the machine info data


***YourComponent.ts***
```typescript
import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { UserService, MachineInfo } from './services/user.service';

export class YourComponent implements OnInit, OnDestroy {
  machineInfo$ = this.userService.machineInfo$;
  machineInfo: MachineInfo | null = null;
  private subscription = new Subscription();

  constructor(private userService: UserService) {}

  ngOnInit(): void {
    // Subscribe to changes
    this.subscription.add(
      this.machineInfo$.subscribe(info => {
        this.machineInfo = info;
        if (info) {
          console.log('Machine info updated:', info);
          // Do something with the data
          this.handleMachineInfoUpdate(info);
        }
      })
    );
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  private handleMachineInfoUpdate(info: MachineInfo): void {
    // Custom logic when machine info updates
    console.log(`Hello ${info.user_id} on ${info.machine_name}`);
  }
}
```