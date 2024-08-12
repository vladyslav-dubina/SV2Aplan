module interface_parametr(input my_interface intf);
    always begin
        intf.clk = ~intf.clk;
    end

    initial begin
        intf.clk = 0;
        intf.reset_n = 0;
        intf.data_in = 0;
        intf.data_out = 0;
        intf.valid = 0;
        intf.ready = 0;
        intf.reset_n = 1;
    end

endmodule