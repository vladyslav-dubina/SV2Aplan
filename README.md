# Translator from the System verilog language to the AVM algebraic model

## Version 1.1

## Instalation
<details><summary>Click to expand</summary>
  
1. Install Python>=3.10.12 on your system
2. Install the necessary libraries:

       pip install -r requirements.txt

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

## Console log example

<details><summary>Click to expand</summary>

![image](https://github.com/vladyslav-dubina/SV2Aplan/assets/82110791/5b8bf515-4038-412a-9457-df555dcaea3a)

</details>


## Elements tranlation

<details><summary>Click to expand</summary>

### Module

| SV CODE                                                                                                     |                                                 APLAN CODE                                                  |                                                                                                              EXAMPLE LINKS |
| :---------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------: | ------------------------------------------------------------------------------------------------------------------------: |
| ![image](https://github.com/vladyslav-dubina/SV2Aplan/assets/82110791/a7dec8f0-b922-4ea4-bbcd-8f501f91d6d1) | ![image](https://github.com/vladyslav-dubina/SV2Aplan/assets/82110791/8579a72d-6b31-4ace-aa43-0dd5dc907711) | [sv_example.sv](examples/sv_example_1/sv_example_1.sv) - [project.env_descript](examples/sv_example_1/aplan/project.env_descript) |

|                                                                                                                                                      DESCRIPTION                                                                                                                                                      |
| :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| As you can see, module is converted to agent_type, the attributes of which are all module arguments from SV. After that we declare the agent (in the picture module_1) the index in the name of the agent depends on the order of the module in the SV code, the type of the agent is agent_type what is this module. |

### Out-of-block declaration
| SV CODE | APLAN CODE | EXAMPLE LINKS |
| ------- | ---------- | ------------ |
| ![image](https://github.com/vladyslav-dubina/SV2Aplan/assets/82110791/4ecbc152-7a63-4333-9ee1-7d722c4e2fa8) | ![image](https://github.com/vladyslav-dubina/SV2Aplan/assets/82110791/c34afd77-98d8-4d4e-abab-20cb2d3db698) | [sv_example.sv](examples/sv_example_1/sv_example_1.sv) - [project.env_descript](examples/sv_example_1/aplan/project.env_descript)|

| DESCRIPTION |
| ----------- |
| As you can see in the picture with the SV code example, the out-of-block declaration (in the reg example, the same translation behavior for wire) will be converted into an attribute in the middle of agent_type from module |

### Out-of-block declaration with assign

| SV CODE | APLAN CODE | EXAMPLE LINKS |
| ------- | ---------- | ------------ |
| ![image](https://github.com/vladyslav-dubina/SV2Aplan/assets/82110791/4ecbc152-7a63-4333-9ee1-7d722c4e2fa8) | ![image](https://github.com/vladyslav-dubina/SV2Aplan/assets/82110791/c34afd77-98d8-4d4e-abab-20cb2d3db698) | [sv_example.sv](examples/sv_example_1/sv_example_1.sv) - [project.env_descript](examples/sv_example_1/aplan/project.env_descript)|

**STATEMENTS**
- [x] always @ ()
- [x] always @ *
- [x] always_comb
- [x] always_ff
- [x] always_latch
- [x] if ()

**ASSERT**
- [x] assert ()
- [x] assert property ()
> with an empty property 

**OPERATIONS**

- All types of logical and arithmetic operations

</details>

## Authors

- [Vlad Dubina](https://github.com/vladyslav-dubina)

- [Volodymyr Peschanenko](https://github.com/VolodymyrPeschanenkoLitSoft)
