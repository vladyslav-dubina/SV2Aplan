
module main;
    import my_package::*;

    state_t current_state;

    int sum;
    
    initial begin
        sum = add(5, 7);

        current_state = RUNNING;
        MAX_COUNT = MAX_COUNT + 1;
    end

endmodule
