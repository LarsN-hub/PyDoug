def main() -> None:
    
    win_obj = open("requirements_win.txt")
    lin_obj = open("requirements_linux.txt")
    mac_obj = open("requirements_mac.txt")
    win_lines: list[str] = win_obj.readlines()
    lin_lines: list[str] = lin_obj.readlines()
    mac_lines: list[str] = mac_obj.readlines()
    win_obj.close()
    lin_obj.close()
    mac_obj.close()
    
    print("\nItems unique to Windows:\n")
    for line in win_lines:
        
        if line not in lin_lines and line not in mac_lines:
            
            print(f"{line}")
            
    print("\nItems unique to Linux:\n")
    for line in lin_lines:
        
        if line not in win_lines and line not in mac_lines:
            
            print(f"{line}")
            
    print("\nItems unique to Mac:\n")
    for line in mac_lines:
        
        if line not in win_lines and line not in lin_lines:
            
            print(f"{line}")
            
    print("\nItems shared only between Windows and Linux:\n")
    for line in win_lines:
        
        if line not in mac_lines and line in lin_lines:
            
            print(f"{line}")
            
    print("\nItems shared only between Windows and Mac:\n")
    for line in win_lines:
        
        if line in mac_lines and line not in lin_lines:
            
            print(f"{line}")
            
    print("\nItems shared only between Mac and Linux:\n")
    for line in mac_lines:
        
        if line not in win_lines and line in lin_lines:
            
            print(f"{line}")

if __name__ == "__main__":
    
    main()