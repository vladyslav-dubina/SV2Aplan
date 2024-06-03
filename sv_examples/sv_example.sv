module register_write_once_example
(
input [15:0] Data_in,
input Clk, // якщо без типу і розміру це bool
input ip_resetn,
input global_resetn,
input write,
output reg [15:0] Data_out // x bits 16
);

reg Write_once_status;

always @(posedge Clk or negedge ip_resetn)
    if (~ip_resetn)
        begin
            Data_out <= 16'h0000; //треба Sensetive для кожного якщо <=
            Write_once_status <= 1'b0;
        end
    else if (write & ~Write_once_status)
        begin
            Data_out <= Data_in & 16'hFFFE;
            Write_once_status <= 1'b1; // Write once status set on first write, independent of input
        end
    else if (~write)
    begin
        Data_out[15:1] <= Data_out[15:1]; // x(1,14) у нас 
        Data_out[0] <= Write_once_status; // x(0,1)
    end

endmodule
