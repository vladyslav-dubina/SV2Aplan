module case_example (
    input logic [1:0] mode,
    input logic [3:0] a,
    input logic [3:0] b,
    output logic [3:0] result
);

    always_comb begin
        case (mode)
            2'b00: result = a + b;
            2'b01: result = a - b;
            2'b10: result = a * b;
            2'b11: result = a & b;
            default:begin result = 4'h0; 
                          result = a & b; 
                     end
        endcase
    end

endmodule