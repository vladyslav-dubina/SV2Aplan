
module main;
    import my_package::*;

    state_t current_state;

    int sum;
    int sum_2;
    
    initial begin
        sum = add(5, 7);

        current_state = RUNNING;
        sum_2 = MAX_COUNT + 1;
    end

endmodule
