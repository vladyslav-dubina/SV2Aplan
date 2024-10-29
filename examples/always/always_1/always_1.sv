module always_1
(
output reg [15:0] Data_out
);

reg Write_once_status;

always_comb
        begin
            Data_out[15:1] <= Data_out[15:1];
            Data_out[0] <= Write_once_status;
        end

endmodule