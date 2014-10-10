use std::os;
use std::rand::{task_rng, Rng};
use std::num::abs;
use std::comm;
use std::sync::Arc;
use std::collections::{PriorityQueue, HashSet};
use std::io::File;

static TASK_NUM: uint = 16;  // 线程数，设为 1 为单线程

type A = u8;
type Shape = (A, A);
type Matrix = Vec<A>;


#[deriving(Clone, Eq, PartialEq)]
enum Step {
    Start,
    Select,
    Up,
    Right,
    Down,
    Left,
}


#[deriving(Clone)]
struct Node {
    matrix: Arc<Matrix>,
    shape: Shape,
    center: A,
    value: uint,
    parent: Option<Arc<Node>>,
    delay: Option<(A, A)>,
    step: Step,
    depth: uint,
}

impl Eq for Arc<Node> {}
impl Eq for Node {}
impl PartialEq for Node {
    fn eq(&self, _: &Node) -> bool {
        false
    }
}
impl PartialEq for Arc<Node> {
    fn eq(&self, _: &Arc<Node>) -> bool {
        false
    }
}
impl PartialOrd for Node {
    fn lt(&self, other: &Node) -> bool {
        self.value > other.value
    }
}
impl PartialOrd for Arc<Node> {
    fn lt(&self, other: &Arc<Node>) -> bool {
        self.value > other.value
    }
}
impl Ord for Node {
    fn cmp(&self, other: &Node) -> Ordering {
        let result = other.value.cmp(&self.value);
        match result {
            Equal => other.depth.cmp(&self.depth),
            _ => result,
        }
    }
}
impl Ord for Arc<Node> {
    fn cmp(&self, other: &Arc<Node>) -> Ordering {
        self.deref().cmp(other.deref())
    }
}


impl Node {
    fn new(shape: Shape, matrix: Matrix) -> Node {
        let value = valuation(shape, &matrix);
        Node {
            matrix: Arc::new(matrix),
            shape: shape,
            center: 0,
            value: value,
            parent: None,
            delay: None,
            step: Start,
            depth: 0,
        }
    }
    fn write_step(&self) {
        let (_, b) = self.shape;
        let mut steps = Vec::new();
        let mut now = self;
        let mut select_num = 0u;
        let mut swap_num = 0u;
        loop {
            steps.push(match now.step {
                Select => {
                    let center = now.center;
                    let pos = (center % b) * 16 + (center / b);
                    let now_swap = swap_num;
                    swap_num = 0;
                    select_num += 1;
                    format!("\r\n{:02X}\r\n{}\r\n", pos, now_swap)
                },
                Left => {swap_num += 1; "L".to_string()},
                Right => {swap_num += 1; "R".to_string()},
                Up => {swap_num += 1; "U".to_string()},
                Down => {swap_num += 1; "D".to_string()},
                Start => break,
            });
            match now.parent {
                Some(ref next) => {now = next.deref();},
                None => fail!("not break???")
            }
        }
        steps.push(format!("{}", select_num));
        let mut file = File::create(&Path::new("solved.txt"));
        steps.reverse();
        for line in steps.iter() {
            match file.write(line.as_bytes()) {Err(r)=>fail!(r), _=>()};
        }
    }
}


fn valuation(shape: Shape, matrix: &Matrix) -> uint {
        let value = matrix.iter().enumerate()
            .map(|(i, v)| point_value(shape, i as int, *v as int))
            .fold(0, |a, b| a + b);
        value as uint
}

fn point_value(shape: Shape, index: int, value: int) -> int {
    let (_, b) = shape;
    let y = b as int;
    abs(index/y - value/y) + abs((index % y) - (value % y))
}


fn swap(parent: Arc<Node>, step: Step) -> Option<Node> {
    let center = parent.center;
    let shape = parent.shape;
    let (a, b) = shape;
    let index = match step {
        Up => if center >= b {Some(center - b)} else {None},
        Down => if center / b < a - 1 {Some(center + b)} else {None},
        Left => if center % b != 0 {Some(center - 1)} else {None},
        Right => if center % b != b - 1 {Some(center + 1)} else {None},
        _ => fail!("Can't swap this step.")
    };
    match index {
        None => None,
        Some(shift) => {
            let i1 = center as int;
            let i2 = shift as int;
            let v1 = *parent.matrix.get(center as uint) as int;
            let v2 = *parent.matrix.get(shift as uint) as int;
            let old_value = parent.value as int;
            let new_value = old_value
                - (point_value(shape, i1, v1) + point_value(shape, i2, v2))
                + (point_value(shape, i1, v2) + point_value(shape, i2, v1));
            Some(Node {
                matrix: parent.matrix.clone(),
                depth: parent.depth + 1,
                parent: Some(parent.clone()),
                center: shift,
                value: new_value as uint,
                step: step,
                delay: Some((center, shift)),
                shape: parent.shape,
            })
        }
    }
}


fn force(delay_node: Arc<Node>) -> Arc<Node> {
    match delay_node.delay {
        None => delay_node,
        Some((a, b)) => {
            let mut matrix = delay_node.matrix.deref().clone();
            let mut node = delay_node.deref().clone();
            matrix.as_mut_slice().swap(a as uint, b as uint);
            node.matrix = Arc::new(matrix);
            node.delay = None;
            Arc::new(node)
        }
    }
}


fn solve_with_node(root: Arc<Node>, max_loop: uint) -> Arc<Node> {
    let mut solutions = Vec::new();
    let mut open = PriorityQueue::with_capacity(max_loop);
    let mut close = HashSet::with_capacity(max_loop);
    open.push(root.clone());
    solutions.push(root.clone());
    let mut solution_value = root.value;
    for _ in range(0, max_loop) {
        match open.pop() {
            None => break,
            Some(delay_node) => {
                let node = force(delay_node);
                let value = node.value;
                if value == solution_value {solutions.push(node.clone());}
                else if value < solution_value {
                    solution_value = value;
                    solutions.clear();
                    solutions.push(node.clone());
                }
                let matrix = node.matrix.deref();
                if !close.contains(matrix) {
                    close.insert(matrix.clone());
                    for step in [Up, Right, Down, Left].iter() {
                        match swap(node.clone(), *step) {
                            Some(new) => open.push(Arc::new(new)),
                            None => ()
                        }
                    }
                }
            },
        };
    }
    solutions.sort_by(|a, b| b.depth.cmp(&a.depth));
    match solutions.pop() {
        None => fail!("Error solve funtion not solution."),
        Some(solution) => solution,
    }
}


fn select(parent: Arc<Node>, center: A) -> Arc<Node> {
    let mut new = parent.deref().clone();
    new.step = Select;
    new.depth += 1;
    new.center = center;
    new.parent = Some(parent.clone());
    Arc::new(new)
}


fn solve_task(node: Arc<Node>, max_loop: uint) -> Arc<Node> {
    let (tx, rx): (Sender<Option<Arc<Node>>>, Receiver<Option<Arc<Node>>>) = comm::channel();
    let mut solutions = PriorityQueue::with_capacity(16);
    let size = node.matrix.len();

    for task_id in range(0, TASK_NUM) {
        let task_tx = tx.clone();
        let task_root = node.clone();
        spawn(proc() {
            let mut sub_solutions = PriorityQueue::with_capacity(size);
            for center in range(0, size) {
                if center % TASK_NUM != task_id {continue};
                let now = select(task_root.clone(), center as A);
                sub_solutions.push(solve_with_node(now, max_loop));
            }
            task_tx.send(sub_solutions.pop())
        });
    }
    for _ in range(0, TASK_NUM) {
        match rx.recv() {
            Some(solution) => solutions.push(solution),
            None => (),
        }
    }
    match solutions.pop() {
        None => fail!("Out solutions heap empty."),
        Some(solution) => solution,
    }
}

fn solve(shape: Shape, matrix: Matrix, max_selection: uint) -> Node {
    let max_loop = 50000u;
    let mut root = Arc::new(Node::new(shape, matrix));

    for select_num in range(0, max_selection) {
        println!("{:2} SELECTION: value {}", select_num, root.value);
        if root.value == 0 {break}
        root = solve_task(root, max_loop);
    }
    root.deref().clone()
}



fn parse() -> (Shape, uint) {
    let args: Vec<String> = os::args();
    if args.len() < 4 {fail!("Lack argument.")}
    let nums: Vec<uint> = args.slice(1, args.len()).iter().map(
        |x| match from_str(x.as_slice().trim()) {
            Some(n) => n,
            None => fail!("Command line parse error, can't convert to int"),
        }
    ).collect();
    let first = *nums.get(0) as A;
    let second = *nums.get(1) as A;
    let third = *nums.get(2);
    ((first, second), third)
}


fn get_matrix(shape: Shape) -> Matrix {
    let (x, y) = shape;
    let size = x as uint * y as uint;
    let mut matrix = Vec::from_fn(size, |id| id as A);
    task_rng().shuffle(matrix.as_mut_slice());
    matrix.shrink_to_fit();
    matrix
}

//fn pos(shape: Shape, n: A) -> uint {
//    let (_, b) = shape;
//    let x = b as uint;
//    let i = n as uint;
//    (i % x) * 0x10 + (i / x)
//}

fn print_matrix(shape: Shape, matrix: &Matrix) {
    let (_, b) = shape;
    let mut i = 0;
    for x in matrix.iter() {
        print!(" {:2}", x);
        if (i+1) % b == 0 {print!("\n\n")}
        i += 1;
    }
}


fn main() {
    let (shape, max_selection) = parse();
    let matrix = get_matrix(shape);
    println!("Input : ")
    print_matrix(shape, &matrix);
    println!("solve...")
    let solution = solve(shape, matrix, max_selection);
    println!("Solution : ");
    print_matrix(shape, solution.matrix.deref());
    println!("depth : {}", solution.depth);
    println!("Write...");
    solution.write_step();
}
