from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object, removeTypeFromForInit


def loop2AplanImpl(
    self: SV2aplan,
    ctx: (
        SystemVerilogParser.Loop_generate_constructContext
        | SystemVerilogParser.Loop_statementContext
    ),
    sv_structure: Structure,
):
    protocol_params = ""
    if self.inside_the_task == True:
        task = self.module.tasks.getLastTask()
        if task is not None:
            protocol_params = "({0})".format(task.parametrs)

    for_decl_identifier = []
    loop_init = "LOOP_INIT_{0}{1};".format(
        Counters_Object.getCounter(CounterTypes.LOOP_COUNTER),
        protocol_params,
    )
    loop_inc = "LOOP_INC_{0}{1};".format(
        Counters_Object.getCounter(CounterTypes.LOOP_COUNTER),
        protocol_params,
    )

    loop_init_flag = True
    loop_inс_flag = True

    if type(ctx) is SystemVerilogParser.Loop_statementContext:
        if ctx.WHILE() or ctx.DO():
            loop_inс_flag = False
            loop_init_flag = False
            loop_init = ""
            loop_inc = ""
        elif ctx.FOR():
            for_initialization_ctx = ctx.for_initialization()
            for_decl_identifier.append(
                self.forInitialization2Apan(for_initialization_ctx, sv_structure)
            )
        elif ctx.FOREACH():
            for_decl_identifier, source_intervals_list = self.loopVarsToAplan(
                ctx.loop_variables(), sv_structure
            )

    beh_index = sv_structure.getLastBehaviorIndex()
    if beh_index is not None:
        sv_structure.behavior[beh_index].addBody(
            (
                None,
                "LOOP_{0}{1}".format(
                    Counters_Object.getCounter(CounterTypes.LOOP_COUNTER),
                    protocol_params,
                ),
                ElementsTypes.PROTOCOL_ELEMENT,
            )
        )

    # LOOP
    beh_index = sv_structure.addProtocol(
        "LOOP_{0}{1}".format(
            Counters_Object.getCounter(CounterTypes.LOOP_COUNTER), protocol_params
        )
    )

    sv_structure.behavior[beh_index].addBody(
        (
            None,
            "({0}LOOP_MAIN_{1}{2})".format(
                loop_init,
                Counters_Object.getCounter(CounterTypes.LOOP_COUNTER),
                protocol_params,
            ),
            ElementsTypes.PROTOCOL_ELEMENT,
        )
    )

    # LOOP MAIN
    beh_index = sv_structure.addProtocol(
        "LOOP_MAIN_{0}{1}".format(
            Counters_Object.getCounter(CounterTypes.LOOP_COUNTER), protocol_params
        )
    )

    # LOOP CONDITION
    condition_name = ""
    if type(ctx) is SystemVerilogParser.Loop_generate_constructContext:
        condition = ctx.genvar_expression().getText()
        (
            action_pointer,
            condition_name,
            source_interval,
            uniq_action,
        ) = self.expression2Aplan(
            condition,
            ElementsTypes.CONDITION_ELEMENT,
            ctx.genvar_expression().getSourceInterval(),
            source_interval=sv_structure,
            name_space_element=ElementsTypes.LOOP_ELEMENT
        )
    elif type(ctx) is SystemVerilogParser.Loop_statementContext:
        if ctx.FOREACH():
            (
                action_pointer,
                condition_name,
            ) = self.loopVarsAndArrayIdentifierToCondition2Aplan(
                for_decl_identifier,
                ctx.ps_or_hierarchical_array_identifier(),
                sv_structure,
            )
        else:
            condition = ctx.expression()
            (
                action_pointer,
                condition_name,
                source_interval,
                uniq_action,
            ) = self.expression2Aplan(
                condition,
                ElementsTypes.CONDITION_ELEMENT,
                sv_structure,
                name_space_element=ElementsTypes.LOOP_ELEMENT
            )

        sv_structure.behavior[beh_index].addBody(
            (
                action_pointer,
                "{1}.(LOOP_BODY_{0}{3};{2}LOOP_MAIN_{0}{3}) + !{1}".format(
                    Counters_Object.getCounter(CounterTypes.LOOP_COUNTER),
                    condition_name,
                    loop_inc,
                    protocol_params,
                ),
                ElementsTypes.ACTION_ELEMENT,
            )
        )

    # LOOP INIT
    if type(ctx) is SystemVerilogParser.Loop_generate_constructContext:
        initialization = ctx.genvar_initialization()
        (
            action_pointer,
            action_name,
            source_interval,
            uniq_action,
        ) = self.expression2Aplan(
            initialization,
            ElementsTypes.ASSIGN_ELEMENT,
            sv_structure,
            name_space_element=ElementsTypes.LOOP_ELEMENT
        )
        loop_init_flag = True
    elif type(ctx) is SystemVerilogParser.Loop_statementContext:
        if ctx.FOREACH():
            action_names_list, action_pointer_list = self.loopVarsDeclarationsToAplan(
                for_decl_identifier, source_intervals_list, sv_structure
            )
        else:
            if loop_init_flag == True:
                
                initialization = ctx.for_initialization()
                (
                    action_pointer,
                    action_name,
                    source_interval,
                    uniq_action,
                ) = self.expression2Aplan(
                    initialization,
                    ElementsTypes.ASSIGN_ELEMENT,
                    sv_structure,
                    name_space_element=ElementsTypes.LOOP_ELEMENT
                )

    if loop_init_flag == True:
        beh_index = sv_structure.addProtocol(
            "LOOP_INIT_{0}{1}".format(
                Counters_Object.getCounter(CounterTypes.LOOP_COUNTER), protocol_params
            )
        )
        if ctx.FOREACH():
            for index, element in enumerate(action_names_list):
                sv_structure.behavior[beh_index].addBody(
                    (action_pointer_list[index], element, ElementsTypes.ACTION_ELEMENT)
                )
        else:
            sv_structure.behavior[beh_index].addBody(
                (action_pointer, action_name, ElementsTypes.ACTION_ELEMENT)
            )

    # LOOP INC
    if type(ctx) is SystemVerilogParser.Loop_generate_constructContext:
        iteration = ctx.genvar_iteration()
        (
            action_pointer,
            action_name,
            source_interval,
            uniq_action,
        ) = self.expression2Aplan(
            iteration,
            ElementsTypes.ASSIGN_ELEMENT,
            sv_structure,
            name_space_element=ElementsTypes.LOOP_ELEMENT
        )
    elif type(ctx) is SystemVerilogParser.Loop_statementContext:
        if ctx.FOREACH():
            action_names_list, action_pointer_list = self.loopVarsToIteration2Aplan(
                for_decl_identifier,
                source_intervals_list,
                sv_structure,
            )
        else:
            if loop_inс_flag == True:
                iteration = ctx.for_step()
                (
                    action_pointer,
                    action_name,
                    source_interval,
                    uniq_action,
                ) = self.expression2Aplan(
                    iteration,
                    ElementsTypes.ASSIGN_ELEMENT,
                    sv_structure,
                    name_space_element=ElementsTypes.LOOP_ELEMENT
                )

    if loop_inс_flag == True:
        beh_index = sv_structure.addProtocol(
            "LOOP_INC_{0}{1}".format(
                Counters_Object.getCounter(CounterTypes.LOOP_COUNTER),
                protocol_params,
            )
        )
        if ctx.FOREACH():
            for index, element in enumerate(action_names_list):
                sv_structure.behavior[beh_index].addBody(
                    (action_pointer_list[index], element, ElementsTypes.ACTION_ELEMENT)
                )
        else:
            sv_structure.behavior[beh_index].addBody(
                (action_pointer, action_name, ElementsTypes.ACTION_ELEMENT)
            )

    # BODY LOOP
    sv_structure.addProtocol(
        "LOOP_BODY_{0}{1}".format(
            Counters_Object.getCounter(CounterTypes.LOOP_COUNTER),
            protocol_params,
        )
    )
    names_for_change = for_decl_identifier
    if type(ctx) is SystemVerilogParser.Loop_generate_constructContext:
        names_for_change += self.body2Aplan(
            ctx.generate_block(), sv_structure, ElementsTypes.LOOP_ELEMENT
        )
    elif type(ctx) is SystemVerilogParser.Loop_statementContext:
        if ctx.FOREACH():
            body_statement = ctx.statement()
        else:
            body_statement = ctx.statement_or_null()
        names_for_change += self.body2Aplan(
            body_statement, sv_structure, ElementsTypes.LOOP_ELEMENT
        )

    Counters_Object.incrieseCounter(CounterTypes.LOOP_COUNTER)
    for element in names_for_change:
        self.module.name_change.deleteElement(element)
