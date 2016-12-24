#version 130
in vec4 p3d_Vertex;
out vec4 texcoord;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main() {
    texcoord = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    gl_Position = texcoord;
}