type N = uint;
type Parent = Option<Box<Node>>;
type Matrix = Box<Vec<N>>;
static X: N = 3;
static Y: N = 3;


enum Step {
    Up,
    Down,
    Left,
    Right,
    Start,
}


struct Node {
    matrix: Matrix,
    shape: (N, N),
    parent: Parent,
    center: N,
    depth: N,
    value: f32,
    step: Step,
}

impl Node {
    fn new(matrix: Matrix, shape: (N, N), center: N) -> Node{
        let value = Node::valuation(&matrix);
        Node {
            matrix: matrix,
            shape: shape,
            parent: None,
            center: center,
            depth: 0,
            value: value,
            step: Start
        }
    }

    fn valuation(matrix: &Matrix) -> f32 {
        0.0f32
    }
}


fn main() {
}
