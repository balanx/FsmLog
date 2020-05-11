
module filt4 (
  output reg   y = 1'd0,
  input        i,

  input    rst_n,
  input    clk
);

reg [3:0] cnt = 4'd0;

localparam
Z0 = 2'd0,
Z1 = 2'd1,
E0 = 2'd2,
E1 = 2'd3;

reg [1:0] state1, next1;
always @(posedge clk or negedge rst_n)
if (!rst_n)
  state1 <= Z0;
else
  state1 <= next1;


always @(*) begin
  next1 = state1;

  case(state1)
    Z0 :
      if (i==1'b1)
        next1 = Z1;
    Z1 :
      if (cnt>4'd9)
        next1 = E0;
      else if (i==1'b0)
        next1 = Z0;
    E0 :
      if (i==1'b0)
        next1 = E1;
    E1 :
      if (cnt>4'd9)
        next1 = Z0;
      else if (i==1'b1)
        next1 = E0;
    default :
        next1 = Z0;
  endcase
end

always @(posedge clk or negedge rst_n)
if (!rst_n) begin
  y <= 1'd0;
  cnt <= 4'd0;
end
else begin
//y <= 1'd0;
  cnt <= 4'd0;

  case (state1)
    Z0 : begin
        y <= 1'b0;
      end
    E0 : begin
        y <= 1'b1;
      end
    Z1 : begin
        cnt <= cnt + 1'b1;
      end
    E1 : begin
        cnt <= cnt + 1'b1;
      end

  endcase
end

endmodule // @FsmLog
