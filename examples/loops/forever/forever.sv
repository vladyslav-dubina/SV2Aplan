module forever_example (
    input logic clk,
    input logic reset_n,
    output logic [3:0] counter
);

    // Internal signal for counter
    logic [3:0] count;

    // Sequential logic with forever loop
    initial begin
        count = 4'b0000;
        forever begin
            @(posedge clk); // Wait for each positive edge of the clock
            if (!reset_n) begin
                count = 4'b0000; // Reset counter if reset is low
            end else begin
                count = count + 1; // Increment counter
            end
        end
    end

    // Assign internal counter to output
    assign counter = count;

endmodule