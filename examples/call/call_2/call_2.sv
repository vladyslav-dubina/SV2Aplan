
module call_2(input clk , input rst , input EP , input CP , output [4:0] PC_OUT);
wire [4:0] MAR_OUT_w ;
wire[4:0] bus_5;
wire [4:0] bus_5_1;
wire EP_w , CP_w ,  LM_w ;
PC_4 UUT1 (.clk(clk) , .rst(rst) , .EP(EP_w) , .CP(CP_w) , .PC_OUT(bus_5));
MAR UUT2(.clk(clk) , .LM(LM_w) , .MAR_IN(bus_5 | bus_5_1) , .MAR_OUT(MAR_OUT_w));
endmodule
 
module PC_4(input clk , input rst , input EP , input CP , output [4:0] PC_OUT);
reg [4:0] PC_OUT_r;
assign PC_OUT = EP ? PC_OUT_r : 5'h00;
always@(posedge clk or posedge rst)
    begin
        if(rst)
            PC_OUT_r <= 5'b00000;
        else if(CP)
            PC_OUT_r <= PC_OUT_r + 1'b1;
    end
endmodule
 
 
module MAR(input clk , input LM , input [4:0] MAR_IN , output [4:0] MAR_OUT);
reg[4:0]MAR_r;
assign MAR_OUT = MAR_r;
always@(posedge clk)
    begin
        if(~LM)
            MAR_r <= MAR_IN;
    end
endmodule