# Translator from the System verilog language to the AVM algebraic model

## Instalation
<details><summary>Click to expand</summary>
  
1. Install Python on your system
2. Install the necessary libraries: ```pip install -r requirements.txt```

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
  
      python sv2aplan_tool.py example.sv 

- An example of using the tool from the resulting path (if the path does not exist, it will be created)

      python sv2aplan_tool.py example.sv my_result_path
      
</details>

