// plate_20x40x1_x: 20x40x1, 外框边宽 3 + 对角筋宽 3 (同 build_stl.py)
W=20; H=40; T=1; RIB=3;
linear_extrude(T) {
  difference() { square([W,H],center=true); square([W-2*RIB,H-2*RIB],center=true); }
  intersection() {
    square([W,H],center=true);
    for (s=[-1,1]) rotate(s*atan2(H,W)) square([2*sqrt(W*W+H*H),RIB],center=true);
  }
}
