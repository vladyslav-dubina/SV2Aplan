module repeat_example (
    input logic clk,
    input logic reset_n,
    output logic done
);

  // Signal declaration
  logic [3:0] count;
  logic start;

  // Initial block with repeat statement
  initial begin
    done = 0;
    start = 0;
  end


endmodule
