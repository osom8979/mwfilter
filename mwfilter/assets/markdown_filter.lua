function Link(elem)
    if not string.match(elem.target, "%.md$") and
        not string.match(elem.target, "^https?://") and
        not string.match(elem.target, "^#") then

        ---@type string
        local anchor = string.match(elem.target, "#.*")
        if anchor then
            elem.target = string.gsub(elem.target, "#.*", "") .. ".md" .. anchor
        else
            elem.target = elem.target .. ".md"
        end
    end
    return elem
end
