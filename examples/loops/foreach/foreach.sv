module foreach_example (
    input logic [7:0] data [0:15],
    output logic [7:0] sum
);

    always_comb begin
        sum = 8'h00;
        foreach (data[i]) begin
            sum = sum + data[i];
        end
    end

endmodule
