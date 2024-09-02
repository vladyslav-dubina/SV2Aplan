interface my_interface(input bit clk);
    logic clk;
    logic reset_n;
    logic [7:0] data_in;
    logic [7:0] data_out;
    logic valid;
    logic ready;
endinterface