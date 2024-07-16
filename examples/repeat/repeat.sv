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
    repeat (5) @(posedge clk); // Wait for 5 clock cycles
    start = 1;
  end

  // Counter logic
  always_ff @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
      count <= 0;
      done <= 0;
    end else if (start) begin
      if (count < 10) begin
        count <= count + 1;
      end else begin
        done <= 1; // Indicate that the counting is done
      end
    end
  end

endmodule
