# Translator from the System verilog language to the AVM algebraic model

## Version 1.5

## Instalation
<details><summary>Click to expand</summary>
  
1. Install Python>=3.10.12 on your system
2. Install the necessary libraries:

       pip install -r requirements.txt

3. For developmers:

      - Ubuntu/Mac OS: ```chod +x scripts/setup_hooks.sh```
      - ```./scripts/setup_hooks.sh```

</details>

## Usage

<details><summary>Click to expand</summary>

**Arguments**
- This tool has some mandatory and optional arguments and parametrs
    - Mandatory argument is ```path_to_sv``` Path to system verilog(.sv) file.
    - Optional parametr ```-rpath``` - Path to result folder. If not entered, the "results" folder will be created.
 
- You can review the available arguments and commands by using the ```-h``` parametr

**Usage examples**

- An example of using the tool without specifying the resulting path (the standard path will be used, that is, the "results" folder, if it does not exist, it will be created)
  
      python scripts/sv2aplan_tool.py example.sv 

- An example of using the tool from the resulting path (if the path does not exist, it will be created)

      python scripts/sv2aplan_tool.py example.sv my_result_path
      
</details>

## Console log example

<details><summary>Click to expand</summary>

![image](https://github.com/vladyslav-dubina/SV2Aplan/assets/82110791/5b8bf515-4038-412a-9457-df555dcaea3a)

</details>

## Elements that are translated in Aplan

You can read more about the transposition of elements in [this file](https://github.com/vladyslav-dubina/SV2Aplan/blob/SV2Aplan_stable/SV%20to%20Aplan%20Progress.docx)

## Authors

- [Vlad Dubina](https://github.com/vladyslav-dubina)

- [Volodymyr Peschanenko](https://github.com/VolodymyrPeschanenkoLitSoft)
