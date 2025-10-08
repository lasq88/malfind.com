---
title: "Revisiting Code Injection #1. Classic DLL injection"
date: 2020-04-20 14:13:19
draft: false
categories: ['C', 'Development', 'Malware analysis']
---

Lately I am involved in a project that requires me to write some C/C++ code. As my C++ is very rusty, I tried to sharpen it a little by doing these small development tasks. Since I am also involved in some reversing of a code using DLL injection techniques, I thought it would be a good idea to understand DLL injection better by writing some injectors myself. I will start with a simplest, classical DLL injection through LoadLibraryA call via CreateRemoteThread.

<!--more-->

## Little bit of theory

So let's quickly explain how the traditional DLL injection technique works. What a DLL injection is anyway? In general code injection happens when one process runs a code in the address space of another process. DLL injection is a specific subset of these techniques when process is forced to load and execute an external DLL. There can be many reasons for performing DLL injection, a lot of applications does it for completely legitimate reasons (for example antiviruses but not only). It is also a very common technique for a malware, usually used to either hide the code in other common process or to hook some functions in other process to steal information. There are some DLL injection techniques which can also be used for persistence or privilege escalation but we won't talk about them here.

Classical DLL Injection relies on few Windows API calls to perform an Injection. It first needs to allocate some memory in target process. It can be done via [VirtualAllocEx](https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualallocex) call. When the memory is allocated, we want to write our injected DLL path into it. This is done via [WriteProcessMemory](https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory) call. When DLL path is written into the memory of victim process, we want to call a [LoadLibraryA](https://docs.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibrarya) function in the context of our victim process. This can be done by spawning a new thread in the target process using [CreateRemoteThread](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createremotethread) call. The LoadLibraryA pointer is passed to CreateRemotethread, together with a pointer to a place in memory where DLL path is stored. That's it. Now our victim will load a malicious binary into memory and execute it.

In short, following steps have to be accomplished to Inject DLL into another process:

1. Store a malicious DLL on disk
2. Find target process ID
3. Allocate memory in the target process with VirtualAllocEx
4. Write the DLL path into memory with WriteProcessMemory
5. Find LoadLibraryA memory address with [GetProcAddress](https://docs.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getprocaddress)
6. Create a remote thread in the victim process by using CreateRemoteThread call with a pointer to LoadLibraryA and another pointer to DLL path sored in memory as argument

That's it. This is a simplest way to inject a DLL into another process. It has of course its downsides. Biggest of all is having to store DLL on the disk before it is injected - this might trigger antivirus software as well as leave additional artifacts on the disk. If we want to avoid this, we need to use a different DLL injection technique (for example Reflective DLL injection which I will cover in separate article).

## Let's code!

So we already know the theory, but theory can be a little hard to understand without actually trying to implement this ourselves.

## DLL code

First of all we will need some DLL to inject into the victim process. I've opted for a very simple DLL that will just pop-up a message box with a name of it's current running process. This will give us a clear indication if the injection has succeeded.

```
#include "pch.h"
#include <Windows.h>
#include <psapi.h>
#include <winuser.h>

BOOLEAN WINAPI DllMain(IN HINSTANCE hDllHandle,
    IN DWORD     nReason,
    IN LPVOID    Reserved)
{
    BOOLEAN bSuccess = TRUE;

    switch (nReason)
    {
    case DLL_PROCESS_ATTACH:

        wchar_t wnameProc[MAX_PATH];
        if (GetProcessImageFileNameW(GetCurrentProcess(), wnameProc, sizeof(wnameProc) / sizeof(*wnameProc)) == 0) {
            bSuccess = FALSE;
        }
        else
        {
            MessageBoxW(NULL, wnameProc, L"Process name", MB_ICONINFORMATION);
            bSuccess = TRUE;
        }

        break;

    case DLL_PROCESS_DETACH:

        break;
    }
    return bSuccess;
}
```

This is a pretty simple DLL. It only consists of DllMain (line 6) which is the main function of DLL library. It doesn't declare any exported functions (which is what legitimate DLLs normally do). DllMain code is executed right after DLL is loaded into the process memory. This is important in the context of DllInjection, as we are looking for simplest way to execute code in the context of other process. That is why most of malicious Dlls which are being injected have most of the malicious code in DllMain. There are ways to force a process to run exported function, but writing your code in DllMain is usually the simplest solution to get code execution.

Our DllMain is quite straightforward. It uses the [GetProcessImageFileNameW](https://docs.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessimagefilenamew) together with [GetCurrentProcess](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getcurrentprocess) API to retreive a name of currently running process. Then it displays a retrieved value in a pop-up MessageBox. When run in injected process it should display victim process name, so we will know that injection was successful. Now we can compile it and put it in a directory of our choice.

## Injector code

Now we only need a code which will inject this library into the process of our choosing. We already have a recipe for this a few paragraphs above, so let us cook some code.

```
int main()
{
    DWORD pid;
    HANDLE hProcess;
    LPVOID lpBaseAddress;
    const char* dllName = "C:\\Users\\username\\source\\repos\\Dll_test\\x64\\Debug\\Dll_test.dll";
    size_t sz = strlen(dllName);
    pid = findProcessID();
    hProcess = OpenProcess(PROCESS_ALL_ACCESS, TRUE, pid);
    lpBaseAddress = VirtualAllocEx(hProcess, NULL, sz, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    WriteProcessMemory(hProcess, lpBaseAddress, dllName, sz, NULL);
    HMODULE hModule = GetModuleHandle(L"kernel32.dll");
    LPVOID lpStartAddress = GetProcAddress(hModule, "LoadLibraryA");
    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)lpStartAddress, lpBaseAddress, 0, NULL);
    if (hThread)
    {
        printf("Injection successful!\n");
    }
    else
    {
        printf("Injection unsuccessful!\n");
    }
}
```

This is our main injector function. It's pretty simple as you can see. The main logic is in lines 8-14. These 7 lines correspond to 6 steps described before for successful DLL injection. Let's analyze them one by one:

**Line 8:** Here we execute a function to find our victim process. We can also create a new process to inject to, but in this case we will just go through the list of running processes. Function listing below

```
DWORD findProcessID()
{
    HANDLE hProcessSnap;
    HANDLE hProcess;
    PROCESSENTRY32 pe32;
    DWORD dwPriorityClass;

    hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    pe32.dwSize = sizeof(PROCESSENTRY32);
    if (!Process32First(hProcessSnap, &pe32))
    {
        CloseHandle(hProcessSnap);
        return(FALSE);
    }

    do {
        if (!wcscmp(pe32.szExeFile, L"notepad.exe")) {
            return pe32.th32ProcessID;
        }

    } while (Process32Next(hProcessSnap, &pe32));
    return 0;
}
```

It creates a snapshot of currently running processes by using [CreateToolhelp32Snapshot](https://docs.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot) API call (line 8) and then iterate through the list of [PROCESSENTRY32](https://docs.microsoft.com/en-us/windows/win32/api/tlhelp32/ns-tlhelp32-processentry32) structures via [Process32Next](https://docs.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-process32next) call (line 21). If executable name (szExeFile) matches the one we are looking for (in this case "notepad.exe") it returns its process ID.

**Line 9:** Once we have PID of our victim process, we need to open a handle to it. We do it by passing just obtained PID to [OpenProcess](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess) call. This will return a handle (hProcess) to the opened process which will allow us to perform further operations on this process.

**Line 10:** Now we have a victim process opened, let's start the injection. As we remember from the theory section, first step to perform injection is to allocate some virtual process memory. We perform this task by using [VirtualAllocEx](https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualallocex) call. It takes 5 parameters:

1. A handle to the opened process: we obtained it in the previous step - this is our hProcess variable
2. The pointer that specifies a desired starting address for the region of pages that you want to allocate. This is best left NULL to let Windows determine best address to allocate.
3. The size of the region of memory to allocate, in bytes. This is equal to the length of a string we want to allocate.
4. The type of memory allocation. We need to bot reserve and commit a memory region (to be able to write to it) hence MEM\_COMMIT | MEM\_RESERVE
5. The memory protection for the region of pages to be allocated. PAGE\_EXECUTE\_READWRITE means this region can be read, written to and executed.

**Line 11:** Once we have a memory region allocated we need to write a path to our DLL to it. We have yet another windows API call for that: [WriteProcessMemory](https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory). It takes 5 arguments:

1. A handle to the opened process. This is same handle we used in previous step.
2. A pointer to the base address of a memory region to write into. It was returned in the last step by VirtualAllocEx (if allocation was successful).
3. A pointer to the buffer that contains data to be written in the address space of the specified process. We pass the dllName variable which is a pointer to a string holding our dll path and name.
4. Size of the buffer (length of our string in this case).
5. A pointer to a variable that receives the number of bytes transferred into the specified process. This is not needed in our code so we can leave it as NULL.

At this point we should already have written our string into the memory of the victim process. We can check that by setting a breakpoint at line 11 and running our program in a debug mode (open notepad.exe first if you are targeting it).

![](/images/2020/04//image-1-1024x353.png)

After our program stopped at the breakpoint, we can see in variables BaseAddress of the allocated memory. In this case it is:

```
lpBaseAddress = 0x000001dd5d7b0000
```

If we now step over once (F10 in Visual Studio), this memory should be written over with our DLL path. We can check that by attaching a debugger to notepad.exe or simply by looking at this memory region in Process Hacker

![](/images/2020/04//image-2.png)

So the memory in the remote process has been successfully written into. Now we can proceed into the next step. Injecting our DLL.

**Line 12/13:** Before we finally inject and run our code - we need a memory address of LoadLibraryA, as this will be an API call that we will execute in the context of the victim process to load our DLL. To get a current address of LoadLibraryA we first need to get a handle to kernel32.dll library, which exports LoadLibraryA. We do it with GetModuleHandle call (line12). After we get a handle to kernel32, we can pass it to GetProcAddress call to obtain a memory address of LoadLibraryA (line13).

**Line 14:** The most important line of code. We call [CreateRemoteThread](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createremotethread) to run a remote thread in the context of our victim process. We pass 7 arguments:

1. Handle to our victim process. Same as previously.
2. Security descriptor for a new thread, can be left as NULL for default values.
3. Initial stack size. 0 for default.
4. A pointer to the function that will be executed by the thread. This is where all the magic happens. We pass a pointer to LoadLibraryA so this function will get executed in the context of the victim process.
5. A pointer to a variable to be passed to the thread function. We pass a pointer to the memory region holding a path to our DLL. This way LoadLibraryA will be executed with our library path as a parameter.
6. Creation flags. We use 0 to run a thread immediately. Some code injection techniques (Process Hollowing which I will hopefully cover in a separate article in the future) requires this to be set as **CREATE\_SUSPENDED** which will create a thread in a suspended state. **CREATE\_SUSPENDED** can also be used to debug issues with a new thread. So we can spawn a new suspended thread, attach a debugger to the process, set a breakpoint and resume the thread. In this case we just set 0 to run a thread immediately.
7. A pointer to a variable that receives the thread identifier. Not needed in this case so it can be set as NULL.

So that's the entire code of the injector. Pretty simple right? Let's see how (if) it runs.

## Let's inject!

So finally after we understood entire code of the injector, we can test it. Let's first launch a notepad.exe instance and then execute our program.

<figure>

![](/images/2020/04//image-4.png)

<figcaption>

It works!

</figcaption>

</figure>

Seems it worked. To verify our DLL is indeed injected into notepad.exe process we can use Process Hacker.

<figure>

![](/images/2020/04//image-5.png)

<figcaption>

  
Injected DLL

</figcaption>

</figure>

It seems our simple injection worked! This is just a simplest way to inject a DLL to another process but in many cases it is sufficient and very useful. It has its downfalls though so in next articles I will try to explain more advanced code injection techniques.

## Code

Traditionally code from this article can be found on my GitHub:

[https://github.com/lasq88/CodeInjection/tree/master/ClassicDllInjection](https://github.com/lasq88/CodeInjection/tree/master/ClassicDllInjection)

## Resources

Useful resources that explain this better then I did:

[https://www.elastic.co/blog/ten-process-injection-techniques-technical-survey-common-and-trending-process](https://www.elastic.co/blog/ten-process-injection-techniques-technical-survey-common-and-trending-process)

[https://0x00sec.org/t/reflective-dll-injection/3080](https://0x00sec.org/t/reflective-dll-injection/3080)

[https://resources.infosecinstitute.com/using-createremotethread-for-dll-injection-on-windows/#gref](https://resources.infosecinstitute.com/using-createremotethread-for-dll-injection-on-windows/#gref)

[https://securityxploded.com/dll-injection-and-hooking.php](https://securityxploded.com/dll-injection-and-hooking.php)

[https://github.com/BenjaminSoelberg/ReflectivePELoader](https://github.com/BenjaminSoelberg/ReflectivePELoader)