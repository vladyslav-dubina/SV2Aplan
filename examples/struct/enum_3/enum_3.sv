typedef enum logic [1:0] {
        IDLE,
        RUNNING,
        STOPPED
} state_t;

module main;

    state_t current_state;
    logic start;

    // Initial block with repeat statement
    initial begin
        current_state = IDLE;
        if (current_state == IDLE) begin
            start = 1;
        end
    end
endmodule
