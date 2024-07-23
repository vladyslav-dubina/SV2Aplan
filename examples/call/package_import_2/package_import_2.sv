
module main;
    import my_package::state_t;
    import my_package::add;
    import my_package::MAX_COUNT;
    state_t current_state;

    int sum;
    
    initial begin
        sum = add(5, 7);

        current_state = RUNNING;

        sum = sum + MAX_COUNT;
    end

endmodule
