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
    for_decl_identifier: str | None = None
    loop_init = "LOOP_INIT_{0};".format(
        Counters_Object.getCounter(CounterTypes.LOOP_COUNTER)
    )
    loop_inc = "LOOP_INC_{0};".format(
        Counters_Object.getCounter(CounterTypes.LOOP_COUNTER)
    )

    loop_init_flag = True
    loop_inс_flag = True

    if type(ctx) is SystemVerilogParser.Loop_statementContext:
        for_initialization_ctx = ctx.for_initialization()
        for_inc_ctx = ctx.for_step()
        if for_inc_ctx is None:
            loop_inс_flag = False
        if for_initialization_ctx is not None:
            for_decl_identifier = self.forInitializationToApan(for_initialization_ctx)
        else:
            loop_init_flag = False

    if loop_init_flag == False:
        loop_init = ""

    if loop_inс_flag == False:
        loop_inc = ""

    beh_index = sv_structure.getLastBehaviorIndex()
    if beh_index is not None:
        sv_structure.behavior[beh_index].addBody(
            (
                "LOOP_{0}".format(
                    Counters_Object.getCounter(CounterTypes.LOOP_COUNTER)
                ),
                ElementsTypes.PROTOCOL_ELEMENT,
            )
        )

    # LOOP
    beh_index = sv_structure.addProtocol(
        "LOOP_{0}".format(Counters_Object.getCounter(CounterTypes.LOOP_COUNTER))
    )

    sv_structure.behavior[beh_index].addBody(
        (
            "({0}LOOP_MAIN_{1})".format(
                loop_init,
                Counters_Object.getCounter(CounterTypes.LOOP_COUNTER),
            ),
            ElementsTypes.PROTOCOL_ELEMENT,
        )
    )

    # LOOP MAIN
    beh_index = sv_structure.addProtocol(
        "LOOP_MAIN_{0}".format(Counters_Object.getCounter(CounterTypes.LOOP_COUNTER))
    )

    # LOOP CONDITION
    condition_name = ""
    if type(ctx) is SystemVerilogParser.Loop_generate_constructContext:
        condition = ctx.genvar_expression().getText()
        condition_name, source_interval, uniq_action = self.expression2Aplan(
            condition,
            ElementsTypes.CONDITION_ELEMENT,
            ctx.genvar_expression().getSourceInterval(),
        )
    elif type(ctx) is SystemVerilogParser.Loop_statementContext:
        condition = ctx.expression().getText()
        condition_name, source_interval, uniq_action = self.expression2Aplan(
            condition,
            ElementsTypes.CONDITION_ELEMENT,
            ctx.expression().getSourceInterval(),
        )

    sv_structure.behavior[beh_index].addBody(
        (
            "{1}.(LOOP_BODY_{0};{2}LOOP_MAIN_{0}) + !{1}".format(
                Counters_Object.getCounter(CounterTypes.LOOP_COUNTER),
                condition_name,
                loop_inc,
            ),
            ElementsTypes.ACTION_ELEMENT,
        )
    )

    # LOOP INIT
    initialization = ""
    if type(ctx) is SystemVerilogParser.Loop_generate_constructContext:
        initialization = ctx.genvar_initialization().getText()
        action_name, source_interval, uniq_action = self.expression2Aplan(
            initialization,
            ElementsTypes.ASSIGN_ELEMENT,
            ctx.genvar_initialization().getSourceInterval(),
        )
        loop_init_flag = True
    elif type(ctx) is SystemVerilogParser.Loop_statementContext:
        if loop_init_flag == True:
            initialization = removeTypeFromForInit(ctx.for_initialization())
            action_name, source_interval, uniq_action = self.expression2Aplan(
                initialization,
                ElementsTypes.ASSIGN_ELEMENT,
                ctx.for_initialization().getSourceInterval(),
            )

    if loop_init_flag == True:
        beh_index = sv_structure.addProtocol(
            "LOOP_INIT_{0}".format(
                Counters_Object.getCounter(CounterTypes.LOOP_COUNTER)
            )
        )
        sv_structure.behavior[beh_index].addBody(
            (action_name, ElementsTypes.ACTION_ELEMENT)
        )

    # LOOP INC
    iteration = ""
    if type(ctx) is SystemVerilogParser.Loop_generate_constructContext:
        iteration = ctx.genvar_iteration().getText()
        action_name, source_interval, uniq_action = self.expression2Aplan(
            iteration,
            ElementsTypes.ASSIGN_ELEMENT,
            ctx.genvar_iteration().getSourceInterval(),
        )
    elif type(ctx) is SystemVerilogParser.Loop_statementContext:
        if loop_inс_flag == True:
            iteration = ctx.for_step().getText()
            action_name, source_interval, uniq_action = self.expression2Aplan(
                iteration,
                ElementsTypes.ASSIGN_ELEMENT,
                ctx.for_step().getSourceInterval(),
            )

    if loop_inс_flag == True:
        beh_index = sv_structure.addProtocol(
            "LOOP_INC_{0}".format(Counters_Object.getCounter(CounterTypes.LOOP_COUNTER))
        )
        sv_structure.behavior[beh_index].addBody(
            (action_name, ElementsTypes.ACTION_ELEMENT)
        )

    # BODY LOOP
    sv_structure.addProtocol(
        "LOOP_BODY_{0}".format(Counters_Object.getCounter(CounterTypes.LOOP_COUNTER))
    )
    names_for_change = [for_decl_identifier]
    if type(ctx) is SystemVerilogParser.Loop_generate_constructContext:
        names_for_change += self.body2Aplan(
            ctx.generate_block(), sv_structure, ElementsTypes.LOOP_ELEMENT
        )
    elif type(ctx) is SystemVerilogParser.Loop_statementContext:
        names_for_change += self.body2Aplan(
            ctx.statement_or_null(), sv_structure, ElementsTypes.LOOP_ELEMENT
        )

    Counters_Object.incrieseCounter(CounterTypes.LOOP_COUNTER)
    for element in names_for_change:
        self.module.name_change.deleteElement(element)
