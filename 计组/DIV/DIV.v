 `timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 2025/04/10 23:16:23
// Design Name: 
// Module Name: DIV
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


module DIV(
    input   [31:0]  dividend,   //被除�?
    input   [31:0]  divisor,    //除数
    input           start,      //启动除法运算
    input           clock,
    input           reset,      //高电平有�?
    output  [31:0]  q,          //�?
    output  [31:0]  r,          //余数
    output reg      busy        //除法器忙标志�?
);
    reg     [4:0]   count;
    reg     [31:0]  reg_q;
    reg     [31:0]  reg_r;
    reg     [31:0]  reg_b;
    reg             r_sign;
    wire [31:0] reg_temp_r;
    wire    [32:0]  sub_add = r_sign? ({reg_r,reg_q[31]} + {1'b0,reg_b}):({reg_r,reg_q[31]} - {1'b0,reg_b}); //加�?�减法器
    assign reg_temp_r = r_sign? reg_r + reg_b : reg_r;
    assign r = dividend[31] ? -reg_temp_r : reg_temp_r;
    assign q = dividend[31] ^ divisor[31] ? -reg_q : reg_q;
    
    always @(posedge clock or posedge reset)
    begin
        if (reset == 1) 
        begin
            count   <=  5'b0;
            busy    <=  0;
        end 
        else 
        begin
            if (start&&(!busy)) 
            begin //初始�?
                reg_r   <= 32'b0;
                r_sign  <= 0;
                reg_q   <= dividend[31] ? -dividend : dividend; //符号扩展
                reg_b   <= divisor[31] ? -divisor : divisor; //符号扩展
                count   <= 5'b0;
                busy    <= 1'b1;
            end 
            else if (busy)
            begin //循环操作
                reg_r   <= sub_add[31:0];   //部分余数
                r_sign  <= sub_add[32];
                reg_q   <= {reg_q[30:0],~sub_add[32]};
                count   <= count + 5'b1;    //计数器加�?
                if (count == 5'b11111) begin
                    busy <= 0;
                end
            end
        end
    end
endmodule
