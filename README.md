# DSI-service

DSI-service was created and tested on Windows 11.

DSI-service is a lightweight flask server that runs in the background on Windows. It provides the machine name and logged in user id to the endpoint "/machine-name".

**_Flask Server Settings:_**

Configurable in /config.json

- Port: 5000
- Endpoint: <http://localhost:5000/machine-name>

**_Response Object_**

```json
{
  "machine_name": "BOBS_COOL_PC",
  "user_id": "BOB"
}
```

---

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

---

## Compile with PyInstaller

1. Open PowerShell or a CMD.

2. Navigate to the root project directory for dsi-service. Make sure you are in the same directory containing DSI-service.py & config.json files.

3. Run one of the two example commands below. Example1 is for a folder build, Example2 is for a stand alone build.

#### Example 1

**Create a folder with all files**

Note: The config.json file is externally configurable with this folder build.

```cmd
pyinstaller --add-data "config.json;." --noconsole DSI-service.py
```

By default, the DSI-service.exe will output to "dist\DSI-service" folder.

The config.json file will be located in "dist\\DSI-service\\\_internal" folder.


#### Example 2

**Create a stand alone .exe file with compiled config inside it**

<span style="color:red">WARNING:</span> You might need to add "dsi-service.exe" to the exceptions list for your antivirus when building the **stand alone .exe** with PyInstaller.

```cmd
pyinstaller --onefile --add-data "config.json;." --noconsole DSI-service.py
```

DSI-service.exe will be in the "dist" folder (config embedded).

**_Batch Files:_** You can also use the .bat files in the root of this project to build a folder version or stand alone version of dsi-service.

- Batch File: build.bat
  - builds the folder version.
- Batch File: build_stand_alone.bat
  - builds the stand alone version.

Both batch scripts will output to versioned folders inside the dist/ directory.

---

## Integrating Angular with DSI-Service.exe

**_Angular Process Flow:_**

1. In the AppComponent's ngOnInit we make the initial call to UserService.

2. The UserService then makes a GET request to the Flask server running at **_localhost:5000/machine-name_**.

3. The response is persisted as a behaviour subject.



**_AppComponent.ts_**

```typescript
import { Component } from '@angular/core';
import { UserService } from './services/user.service';

export class DsiMachineInfo {
    machine_name!: string;
    user_id!: string;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: false,
})
export class AppComponent{

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
                        `Problem fetching machine name.\nMake sure the DSI-Service is running on your Windows computer.\nError: ${errorMsg}`,
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

In the Angular service we are also creating a behavior subject to make the machine info  available for any components needing access to it.

**_UserService.ts_**

```typescript
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { throwError } from 'rxjs/internal/observable/throwError';
import { catchError, tap } from 'rxjs/operators';

export class MachineInfo {
  machine_name!: string;
  user_id!: string;
}

@Injectable({
  providedIn: 'root',
})
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
    return this.http.get<MachineInfo>('http://localhost:5000/machine-name').pipe(tap((machineInfo) => this.setMachineInfo(machineInfo)));
  }
}
```

#### How to subscribe to the behaviour subject in another component

Subscribe to the machine info data

**_HomeComponent.ts_**

```typescript
import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { MachineInfo, UserService } from 'src/app/services/user.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-home',
  imports: [CommonModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
})
export class HomeComponent implements OnInit, OnDestroy {
  machineInfo$ = this.userService.machineInfo$;
  machineInfo: MachineInfo | null = null;
  private readonly subscription = new Subscription();

  constructor(private readonly userService: UserService) {}

  ngOnInit(): void {
    // Subscribe to changes
    this.subscription.add(
      this.machineInfo$.subscribe((info) => {
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

Display the subscribed data in the template file.

**_HomeComponent.html_**


```html
<!-- Show loading message when no data -->
<div *ngIf="!(machineInfo$ | async)">
    <p>Loading machine information...</p>
</div>

<div>
    <p>Machine: {{ (machineInfo$ | async)?.machine_name || 'Not available' }}</p>
    <p>User: {{ (machineInfo$ | async)?.user_id || 'Not available' }}</p>
</div>
```