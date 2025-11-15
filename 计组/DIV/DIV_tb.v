`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2025/04/10 23:16:38
// Design Name: 
// Module Name: DIV_tb
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module DIV_tb();
reg  [31:0]  dividend;
reg  [31:0]  divisor;
reg  start;
reg  clock;
reg  reset;
wire [31:0]  q;
wire [31:0]  r;
wire busy;

DIV uut(dividend, divisor, start, clock, reset, q, r, busy);

initial begin
    clock = 0;
    reset = 1;
    start = 0;
    #10;
    reset = 0;
    dividend = 32'h00000014; // 20  
    divisor = 32'h00000003;  // 3  
    start = 1;   // 结果应为 q=6, r=2
    #10;
    start = 0;
    #150;
    
    reset = 1;
    #10;
    reset = 0;
    dividend = 32'hffffffec; // -20  
    divisor = 32'h00000003;  // 3  
    start = 1;   // 结果应为 q=-6, r=-2
    #10;
    start = 0;
    #150;
    
    reset = 1;
    #10;
    reset = 0;
    dividend = 32'h00000014; // 20
    divisor = 32'hfffffffd;  // -3  
    start = 1;   // 结果应为 q=-6, r=2
    #10;
    start = 0;
    #150;
    
    reset = 1;
    #10;
    reset = 0;
    dividend = 32'hffffffec; // -20  
    divisor = 32'hfffffffd;  // -3
    start = 1;   // 结果应为 q=6, r=-2
    #10;
    start = 0;
    #150;
    
    reset = 1;
    #10;
    reset = 0;
    dividend = 32'h7fffffff; // 2147483647 (最大正数)
    divisor = 32'h00000002;  // 2  
    start = 1;   // 结果应为 q=1073741823, r=1
    #10;
    start = 0;
    #150;
    
    reset = 1;
    #10;
    reset = 0;
end

always #2 clock = ~clock;
endmodule