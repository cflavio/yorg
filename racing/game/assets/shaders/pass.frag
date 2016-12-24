#version 130
in vec2 texcoord;
uniform sampler2D input_tex;
uniform float gamma;
out vec4 p3d_FragColor;

vec4 gamma_correct(vec4 col) {
    vec3 _col = vec3(col);
    return vec4(pow(_col, vec3(1.0 / gamma)), 1.0);
}

void main() {
    p3d_FragColor = gamma_correct(texture(input_tex, texcoord));
}
