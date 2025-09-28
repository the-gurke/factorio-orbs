local constants = {}

function constants.cloud_animation(scale)
    scale = scale or .4
    return {
        filename = '__orbs__/graphics/entity/cloud/cloud-45-frames.png',
        priority = 'low',
        width = 256,
        height = 256,
        frame_count = 45,
        animation_speed = 0.5,
        line_length = 7,
        scale = scale,
        shift = {0.0, 0.75}
    }
end

return constants