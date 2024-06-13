module register_write_once_example
(
input Clk,
input ip_resetn,
input write,
output reg [15:0] Data_out
);

reg Write_once_status;

always @(posedge Clk or negedge ip_resetn)
    if (~ip_resetn) 
        begin
            Data_out[0] <= Write_once_status;
        end
    else if (write & ~Write_once_status)
        begin
            Data_out[0] <= Write_once_status;
        end 
    else if (~write)
        begin
            Data_out[0] <= Write_once_status;
        end
    else
        begin
            Data_out[0] <= Write_once_status;
        end

endmodule