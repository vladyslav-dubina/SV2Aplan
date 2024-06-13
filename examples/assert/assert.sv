module register_write_once_example
(
input Clk,
input ip_resetn,
input write,
output reg [15:0] Data_out
);

reg Write_once_status;

always_comb
        begin
            assert (write & ~Write_once_status && ip_resetn);
        end
assert property (write & ~Write_once_status && ip_resetn);
endmodule